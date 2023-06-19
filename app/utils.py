import os
import re

from flask import current_app
from PIL import Image as PILImage


def get_directory_list():
    basepath = current_app.config["UPLOAD_FOLDER"]
    directories = [
        d for d in os.listdir(basepath) if os.path.isdir(os.path.join(basepath, d))
    ]
    return directories


def parse_data_string(custom_dict_str):
    result = {}

    # Parse parameters
    match = re.search(r"'parameters': '(.*?)\\n", custom_dict_str)
    if match:
        result["parameters"] = match.group(1)

    # Parse negative prompt
    match = re.search(r"\\nNegative prompt: (.*?)\\nSteps:", custom_dict_str)
    if match:
        result["negative_prompt"] = match.group(1)

    # Parse steps
    match = re.search(r"\\nSteps: (.*?),", custom_dict_str)
    if match:
        result["steps"] = int(match.group(1))

    # Parse sampler
    match = re.search(r"Sampler: (.*?),", custom_dict_str)
    if match:
        result["sampler"] = match.group(1)

    # Parse CFG scale
    match = re.search(r"CFG scale: (.*?),", custom_dict_str)
    if match:
        result["cfg_scale"] = float(match.group(1))

    # Parse seed
    match = re.search(r"Seed: (.*?),", custom_dict_str)
    if match:
        result["seed"] = int(match.group(1))

    # Parse size
    match = re.search(r"Size: (.*?),", custom_dict_str)
    if match:
        result["size"] = match.group(1)

    # Parse model hash
    match = re.search(r"Model hash: (.*?),", custom_dict_str)
    if match:
        result["model_hash"] = match.group(1)

    # Parse model
    match = re.search(r"Model: (.*?)'}", custom_dict_str)
    if match:
        result["model"] = match.group(1)

    return result


def get_sd_info(image):
    try:
        with PILImage.open(image) as img:
            sd_metadata = parse_data_string(str(img.text))
            return sd_metadata
    except Exception as e:
        print(f"{image} not readable. Error: {e}")


def create_thumbnail(image_path, directory, size=(300, 300)):
    thumbnail_dir = os.path.join(
        current_app.static_folder, current_app.config["THUMBNAIL_FOLDER"], directory
    )
    os.makedirs(thumbnail_dir, exist_ok=True)
    thumbnail_path = os.path.join(thumbnail_dir, os.path.basename(image_path))
    relative_path = os.path.join(
        current_app.config["THUMBNAIL_FOLDER"], directory, os.path.basename(image_path)
    )
    if not os.path.exists(thumbnail_path):
        with PILImage.open(image_path) as img:
            img.thumbnail(size)
            img.save(thumbnail_path, "JPEG")
    return relative_path
