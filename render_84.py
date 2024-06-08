import bpy
import math
import os
import random
import numpy as np
import cv2
import glob

def make_video(images):
    video_name = images[0].split("_0000")[0].replace("_pngs", "") + ".mp4"
    os.makedirs(os.path.dirname(video_name), exist_ok=True)
    frame = cv2.imread(images[0])
    height, width, layers = frame.shape
    video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'avc1'), 10, (width, height))

    for image in images:
        video.write(cv2.imread(image))

    cv2.destroyAllWindows()
    video.release()

def render_orbit(glb_path, output_dir):
    # Remove Cube (prior objects)
    for obj in bpy.data.objects:
        if obj.type != 'CAMERA' and obj.type != 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    # Background to white
    world = bpy.data.worlds['World']
    world.use_nodes = False
    world.color = (1, 1, 1)  # RGB values for white

    # Load the glb file
    bpy.ops.import_scene.gltf(filepath=glb_path)

    # Get the imported objects
    imported_objects = bpy.context.selected_objects

    for obj in imported_objects:
        if obj.type == 'MESH':
            # Update the object's bounding box
            obj.update_from_editmode()

            # Assign materials to the object if it has material slots
            if obj.material_slots:
                for material_slot in obj.material_slots:
                    material = material_slot.material
                    if material:
                        obj.data.materials.append(material)

    # multiply 3d coord list by matrix
    def np_matmul_coords(coords, matrix, space=None):
        M = (space @ matrix @ space.inverted()
            if space else matrix).transposed()
        ones = np.ones((coords.shape[0], 1))
        coords4d = np.hstack((coords, ones))
        
        return np.dot(coords4d, M)[:,:-1]

    # get the global coordinates of all object bounding box corners    
    coords = np.vstack(
        tuple(np_matmul_coords(np.array(o.bound_box), o.matrix_world.copy())
            for o in
                imported_objects
                if o.type == 'MESH'
                )
            )
    # bottom front left (all the mins)
    bfl = coords.min(axis=0)
    # top back right
    tbr = coords.max(axis=0)

    bbox_size = max(tbr[0]-bfl[0], tbr[1]-bfl[1], tbr[2]-bfl[2])
    bbox_translate_obj = np.array([-(tbr[0]+bfl[0])/2, -(tbr[1]+bfl[1])/2, -(tbr[2]+bfl[2])/2, 1]).reshape((1,4))

    for o in imported_objects:
        if o.type == 'MESH':
            bbox_translate = bbox_translate_obj @ np.asarray(o.matrix_world.copy())[:, :]
            bbox_translate = bbox_translate.reshape((4, 1))
            o.location = (bbox_translate[0], bbox_translate[1], bbox_translate[2])

    # Set the scale and location for each object
    yaw = math.radians(random.uniform(-180, 180))
    
    bpy.ops.transform.rotate(value=yaw)
    bpy.ops.transform.resize(value=((1 / bbox_size, 1 / bbox_size, 1 / bbox_size)))

    # Set up the scene
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 576
    scene.render.resolution_y = 576
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

    # Set up the camera
    cam = bpy.data.objects['Camera']
    cam.rotation_euler = (0, 0, 0)

    cam.data.angle = math.radians(33.7)
    cam_fov = math.radians(cam.data.angle)
    cam_distance = (1 / 2) / math.tan(cam_fov / 2)

    # Set the camera location and focal length
    cam.location = (0, -cam_distance, 0)
    cam.data.lens = cam.data.sensor_width / (1 / cam_distance * 2) # 2 is the lenz parameter

    # Render the 84-frame orbit
    frames = 21
    scene.frame_end = frames - 1
    cam_scale = cam_distance
    elevation_angle = math.radians(random.uniform(-5, 30))

    for i in range(frames):
        scene.frame_set(i)
        angle = i * (2 * math.pi / frames)
        cam.location = (cam_scale * math.sin(angle) * math.cos(elevation_angle),
                        -cam_scale * math.cos(angle) * math.cos(elevation_angle),
                        cam_scale * math.sin(elevation_angle))

        # Calculate the camera's rotation to look at the parent object
        direction = imported_objects[0].location - cam.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam.rotation_euler = rot_quat.to_euler()

        scene.render.filepath = f"{output_dir}/orbit_frame_{i:04d}.png"
        bpy.ops.render.render(write_still=True)

    print("Orbit image rendering completed.")

base_path = os.path.join(os.path.expanduser("~"), ".objaverse")
versioned_path = os.path.join(base_path, "hf-objaverse-v1")
glb_path = os.path.join(versioned_path, "glbs")

cnt = 0
for folder_name in os.listdir(glb_path):
    folder_path = os.path.join(glb_path, folder_name)
    
    # Check if the item is a directory
    if os.path.isdir(folder_path):
        # Find the .glb file inside the folder
        glb_files = [f for f in os.listdir(folder_path) if f.endswith(".glb")]

        cnt = cnt + 1
        print(f"cnt: {cnt}")
        
        for i in range(len(glb_files)):
            glb_file = glb_files[i]
            glb_file_path = os.path.join(folder_path, glb_file)
            
            # Create the output directory for the current folder
            if i == 0:
                output_dir = os.path.join("./object_outputs", folder_name)
            else:
                output_dir = os.path.join("./object_outputs", f"{folder_name}_{i}")

            if os.path.exists(output_dir):
                print(f"passing output_dir: {output_dir}")
                continue

            os.makedirs(output_dir, exist_ok=True)
            
            # Render the orbit for the current .glb file
            render_orbit(glb_file_path, output_dir)
            
            print(f"Processed {folder_name} successfully.")
    else:
        print(f"No .glb file found in {folder_name}.")

# glb_path = os.path.join(versioned_path, "glbs", "000-067", "38cb6584bb734d729baf712da41b141f.glb")

# output_dir = "./objav_outputs"

# # Create the output directory if it doesn't exist
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)

# render_orbit(glb_path, output_dir)