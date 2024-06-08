import os
import cv2
from glob import glob
import numpy as np

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

base_path = os.path.join(os.path.expanduser("~"), ".objaverse")
versioned_path = os.path.join(base_path, "hf-objaverse-v1")
glb_path = os.path.join(versioned_path, "glbs")

for folder_name in os.listdir(glb_path):
    folder_path = os.path.join(glb_path, folder_name)
    
    # Check if the item is a directory
    if os.path.isdir(folder_path):
        # Find the .glb file inside the folder
        glb_files = [f for f in os.listdir(folder_path) if f.endswith(".glb")]
        
        if glb_files:
            for i in range(len(glb_files)):
                glb_file = glb_files[i]
                glb_file_path = os.path.join(folder_path, glb_file)
                
                # Create the output directory for the current folder
                if i==0:
                    output_dir = os.path.join("./object_outputs", folder_name)
                else:
                    output_dir = os.path.join("./object_outputs", f"{folder_name}_{i}")

                png_list = []
                png_files = glob(os.path.join(output_dir, '*.png'))
                for file_path in png_files:
                    png_list.append(file_path)
                png_list.sort()

                if png_list == []:
                    continue
                else:
                    make_video(png_list)
                    # Rename the output video file
                    video_name = f"orbit_frame_{folder_name}.mp4"
                    
                    print(f"Processed {folder_name} successfully.")
        else:
            print(f"No .glb file found in {folder_name}.")