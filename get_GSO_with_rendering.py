import sys, json, requests
import getopt
import os
import zipfile
import shutil
from render_84 import render_orbit

if sys.version_info[0] < 3:
    raise Exception("Python 3 or greater is required. Try running `python3 download_collection.py`")

collection_name = ''
owner_name = ''

# Read options
optlist, args = getopt.getopt(sys.argv[1:], 'o:c:')

sensor_config_file = ''
private_token = ''
for o, v in optlist:
    if o == "-o":
        owner_name = v.replace(" ", "%20")
    if o == "-c":
        collection_name = v.replace(" ", "%20")

if not owner_name:
    print('Error: missing `-o <owner_name>` option')
    quit()

if not collection_name:
    print('Error: missing `-c <collection_name>` option')
    quit()


print("Downloading models from the {}/{} collection.".format(owner_name, collection_name.replace("%20", " ")))

page = 1
count = 0

# The Fuel server URL.
base_url ='https://fuel.gazebosim.org/'

# Fuel server version.
fuel_version = '1.0'

# Path to get the models in the collection
next_url = '/models?page={}&per_page=100&q=collections:{}'.format(page,collection_name)

# Path to download a single model in the collection
download_url = base_url + fuel_version + '/{}/models/'.format(owner_name)

# Create the output directory
output_dir = "./GSO_outputs"
os.makedirs(output_dir, exist_ok=True)

# Iterate over the pages
for i in range(1):
    url = base_url + fuel_version + next_url
    # Get the contents of the current page.
    r = requests.get(url)
    if not r or not r.text:
        break

    # Convert to JSON
    models = json.loads(r.text)
    # Compute the next page's URL
    page = page + 1
    next_url = '/models?page={}&per_page=100&q=collections:{}'.format(page, collection_name)

    # Download each model
    for model in models:
        count += 1
        model_name = model['name']
        print('Downloading (%d) %s' % (count, model_name))
        download = requests.get(download_url + model_name + '.zip', stream=True)

        # Create a temporary directory to extract the ZIP file
        temp_dir = model_name + "_temp"
        os.makedirs(temp_dir, exist_ok=True)

        # Save the ZIP file to the temporary directory
        zip_path = os.path.join(temp_dir, model_name + '.zip')
        with open(zip_path, 'wb') as fd:
            for chunk in download.iter_content(chunk_size=1024*1024):
                fd.write(chunk)

        # Extract the ZIP file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Copy 'texture.png' from ./materials directory to ./meshes directory
        texture_source = os.path.join(temp_dir, "materials", "textures", "texture.png")
        texture_dest = os.path.join(temp_dir, "meshes", "texture.png")
        shutil.copy(texture_source, texture_dest)

        # Call render_orbit function with inputs from ./meshes directory
        obj_path = os.path.join(temp_dir, "meshes", "model.obj")
        mtl_path = os.path.join(temp_dir, "meshes", "model.mtl")
        texture_path = os.path.join(temp_dir, "meshes", "texture.png")
        output_subdir = os.path.join(output_dir, f"output_{count}")
        os.makedirs(output_subdir, exist_ok=True)
        render_orbit(obj_path, texture_path, output_subdir)

        # Remove the temporary directory
        shutil.rmtree(temp_dir)

        print(f"Done {count}.")

print('Done.')