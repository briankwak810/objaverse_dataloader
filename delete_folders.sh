#!/bin/bash

# Set the directory path
directory="./object_outputs"

# Read the folder names from the text file
while read folder; do
    # Delete the folder if it exists
    if [ -d "$directory/$folder" ]; then
        rm -rf "$directory/$folder"
        echo "Deleted folder: $directory/$folder"
    else
        echo "Folder not found: $directory/$folder"
    fi
done < delete_images.txt