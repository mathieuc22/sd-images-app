from PIL import Image
from pathlib import Path
import json

# set the path containing the images
source_path = Path(
    "/home/mathieu/Documents/projects/stable-diffusion-webui/outputs/txt2img-images/2023-05-11/"
)

# default assets folder
base_dir = Path(__file__).parent.resolve()
DB_FILE = base_dir / "db.json"


# Extract sd meta from image
def get_sd_info(image):
    try:
        # read the image data using PIL
        with Image.open(image) as image:
            # extract data
            sd_metadata = image.text
            return sd_metadata
    except:
        print(f"{image.name} not readable")


def main():
    nb_files = len(list(source_path.rglob("*.*")))
    print(f"{nb_files} files in the folder")
    for images in source_path.rglob("*.*"):
        sd_metadata = get_sd_info(images)
        print(json.dumps(sd_metadata))


if __name__ == "__main__":
    main()
