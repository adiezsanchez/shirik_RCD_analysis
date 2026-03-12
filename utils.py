from pathlib import Path
import nd2
import numpy as np

def list_images (directory_path, format=None):

    # Transform directory string into a Path object
    directory_path = Path(directory_path)

    # Create an empty list to store all image filepaths within the dataset directory
    images = []

    # Append file_path
    for file_path in directory_path.glob(f"*{format}"):
        if "f00d0" not in file_path.stem: # ignore tiled images from dataset
            images.append(str(file_path))

    return images

def read_image (image, log=True):
    """Read raw image microscope files (.nd2), apply downsampling if needed and return filename and a numpy array"""

    # Read path storing raw image and extract filename
    file_path = Path(image)
    filename = file_path.stem

    # Extract file extension
    extension = file_path.suffix

    if extension == ".nd2":
        # Read stack from .nd2 (z, ch, x, y) or (ch, x, y)
        img = nd2.imread(image)
        
    else:
        print ("Implement new file reader")

    if log:
        # Feedback for researcher
        print(f"\nImage analyzed: {filename}")

    return img, filename

def extract_img_metadata (img_filepath, verbose = False):
    
    # Extract image metadata from filename
    field_of_view = int(Path(img_filepath).stem.split("_")[5].split("Pos")[1])
    well_id = Path(img_filepath).stem.split("_")[4].split("Well")[1]

    # Create a dictionary containing all image descriptors
    descriptor_dict = {"well_id": well_id, "FOV": field_of_view}

    if verbose:

        print(f"Visualizing well: {well_id}, FOV: {field_of_view}")

    return descriptor_dict