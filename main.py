from flask import Flask, send_from_directory, render_template
import os
from PIL import Image

app = Flask(__name__)
app.config[
    "UPLOAD_FOLDER"
] = "/home/mathieu/Documents/projects/stable-diffusion-webui/outputs/txt2img-images/"


def get_directory_list():
    basepath = app.config["UPLOAD_FOLDER"]
    directories = [
        d for d in os.listdir(basepath) if os.path.isdir(os.path.join(basepath, d))
    ]
    return directories


def get_sd_info(image):
    try:
        # read the image data using PIL
        with Image.open(image) as image:
            # extract data
            sd_metadata = image.text
            return sd_metadata
    except:
        print(f"{image.name} not readable")


@app.route("/")
def index():
    directories = get_directory_list()
    return render_template("index.html", directories=directories)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/galerie/<directory>")
def galerie(directory):
    basepath = os.path.join(app.config["UPLOAD_FOLDER"], directory)
    images = [
        {
            "path": os.path.join(directory, i),
            "metadata": get_sd_info(
                os.path.join(app.config["UPLOAD_FOLDER"], directory, i)
            ),
        }
        for i in os.listdir(basepath)
        if os.path.isfile(os.path.join(basepath, i))
    ]
    return render_template("galerie.html", images=images)
