import math
import os
import random
import numpy as np
from PIL import Image

def inspect_background(input_dir, target_color):
    delete_images = []
    for folder in os.listdir(input_dir):
        folder_path = os.path.join(input_dir, folder)
        images = [f for f in os.listdir(folder_path) if f.endswith(".png")]
        for i in range(len(images)):
            all_pixels_match = False
            # Open the image
            image = Image.open(os.path.join(folder_path, images[i]))
            # Convert the image to RGB mode
            image = image.convert('RGB')
            # Convert the image to a NumPy array
            pixels = np.array(image)
            # Create a mask of pixels that match the target color
            mask = np.all((pixels >= target_color[0] - 4) & (pixels <= target_color[0] + 4), axis=-1)        # Check if all pixels match the target color
            all_pixels_match = np.all(mask)

            if all_pixels_match == True:
                delete_images.append(folder)
                print(folder)
                break

    return delete_images

# input_dir = os.path.join(os.path.expanduser("~"), "Desktop", "3dcv", "objaverse_dataloader", "Objaverse", "object_outputs")
delete_images = inspect_background('./object_outputs', (206, 206, 206))

file_name = './delete_images.txt'

with open(file_name, 'w+') as file:
    for img in delete_images:
        file.write(img + "\n")