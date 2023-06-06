from flask import Flask, render_template, url_for, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from PIL import Image as PILImage
import re
from flask_migrate import Migrate

app = Flask(__name__)
app.config[
    "UPLOAD_FOLDER"
] = "/home/mathieu/Documents/projects/stable-diffusion-webui/outputs/txt2img-images/"
app.config["THUMBNAIL_FOLDER"] = "thumbnails"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(300), nullable=False)
    thumbnail = db.Column(db.String(300), nullable=False)
    parameters = db.Column(db.String(1000))
    negative_prompt = db.Column(db.String(500))
    steps = db.Column(db.Integer)
    sampler = db.Column(db.String(200))
    cfg_scale = db.Column(db.Float)
    seed = db.Column(db.BigInteger)
    size = db.Column(db.String(100))
    model_hash = db.Column(db.String(200))
    model = db.Column(db.String(200))
    liked = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Image {self.path}>"


with app.app_context():
    db.create_all()


def get_directory_list():
    basepath = app.config["UPLOAD_FOLDER"]
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
        app.static_folder, app.config["THUMBNAIL_FOLDER"], directory
    )
    os.makedirs(thumbnail_dir, exist_ok=True)
    thumbnail_path = os.path.join(thumbnail_dir, os.path.basename(image_path))
    relative_path = os.path.join(
        app.config["THUMBNAIL_FOLDER"], directory, os.path.basename(image_path)
    )
    if not os.path.exists(thumbnail_path):
        with PILImage.open(image_path) as img:
            img.thumbnail(size)
            img.save(thumbnail_path)
    return relative_path


@app.route("/")
def index():
    directories = get_directory_list()
    return render_template("index.html", directories=directories)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/galerie/<directory>")
def galerie(directory):
    images = Image.query.filter(
        Image.path.startswith(os.path.join(app.config["UPLOAD_FOLDER"], directory))
    ).all()
    return render_template("galerie.html", images=images)


@app.route("/admin/generate-thumbnails")
def generate_thumbnails():
    for directory in get_directory_list():
        basepath = os.path.join(app.config["UPLOAD_FOLDER"], directory)
        for filename in os.listdir(basepath):
            image_path = os.path.join(basepath, filename)
            if os.path.isfile(image_path):
                thumbnail_path = create_thumbnail(image_path, directory)
                metadata_info = get_sd_info(image_path)
                if metadata_info is not None:
                    # Check if the image already exists in the database
                    image = Image.query.filter_by(path=image_path).first()

                    if image:
                        # Update existing image details
                        image.thumbnail = thumbnail_path
                        image.parameters = str(metadata_info.get("parameters", ""))
                        image.negative_prompt = str(
                            metadata_info.get("negative_prompt", "")
                        )
                        image.steps = metadata_info.get("steps", 0)
                        image.sampler = metadata_info.get("sampler", "")
                        image.cfg_scale = metadata_info.get("cfg_scale", 0.0)
                        image.seed = metadata_info.get("seed", 0)
                        image.size = metadata_info.get("size", "")
                        image.model_hash = metadata_info.get("model_hash", "")
                        image.model = metadata_info.get("model", "")
                    else:
                        # Create a new image record
                        image = Image(
                            path=image_path,
                            thumbnail=thumbnail_path,
                            parameters=str(metadata_info.get("parameters", "")),
                            negative_prompt=str(
                                metadata_info.get("negative_prompt", "")
                            ),
                            steps=metadata_info.get("steps", 0),
                            sampler=metadata_info.get("sampler", ""),
                            cfg_scale=metadata_info.get("cfg_scale", 0.0),
                            seed=metadata_info.get("seed", 0),
                            size=metadata_info.get("size", ""),
                            model_hash=metadata_info.get("model_hash", ""),
                            model=metadata_info.get("model", ""),
                        )
                        db.session.add(image)
    db.session.commit()
    return jsonify(success=True), 200


@app.route("/delete-image/<int:image_id>", methods=["DELETE"])
def delete_image(image_id):
    image = Image.query.get(image_id)
    if image is None:
        return jsonify(success=False), 404

    try:
        os.remove(image.path)  # delete original image
        os.remove(os.path.join(app.static_folder, image.thumbnail))  # delete thumbnail
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

    db.session.delete(image)
    db.session.commit()

    return jsonify(success=True), 200


@app.route("/like-image/<int:image_id>", methods=["POST"])
def like_image(image_id):
    image = Image.query.get(image_id)
    if image is None:
        return jsonify(success=False), 404

    image.liked = True
    db.session.commit()

    return jsonify(success=True), 200


@app.route("/unlike-image/<int:image_id>", methods=["POST"])
def unlike_image(image_id):
    image = Image.query.get(image_id)
    if image is None:
        return jsonify(success=False), 404

    image.liked = False
    db.session.commit()

    return jsonify(success=True), 200


@app.route("/images-with-likes")
def images_with_likes():
    images = Image.query.filter(Image.liked == True).all()
    return render_template("galerie.html", images=images)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
