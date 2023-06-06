import os

from flask import current_app, jsonify, render_template, send_from_directory, url_for

from app import db
from app.models import Image
from app.utils import create_thumbnail, get_directory_list, get_sd_info


@current_app.route("/")
def index():
    directories = get_directory_list()
    return render_template("index.html", directories=directories)


@current_app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@current_app.route("/galerie/<directory>")
def galerie(directory):
    images = Image.query.filter(
        Image.path.startswith(
            os.path.join(current_app.config["UPLOAD_FOLDER"], directory)
        )
    ).all()
    return render_template("galerie.html", images=images)


@current_app.route("/admin/generate-thumbnails")
def generate_thumbnails():
    for directory in get_directory_list():
        basepath = os.path.join(current_app.config["UPLOAD_FOLDER"], directory)
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


@current_app.route("/delete-image/<int:image_id>", methods=["DELETE"])
def delete_image(image_id):
    image = Image.query.get(image_id)
    if image is None:
        return jsonify(success=False), 404

    try:
        os.remove(image.path)  # delete original image
        os.remove(
            os.path.join(current_app.static_folder, image.thumbnail)
        )  # delete thumbnail
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

    db.session.delete(image)
    db.session.commit()

    return jsonify(success=True), 200


@current_app.route("/like-image/<int:image_id>", methods=["POST"])
def like_image(image_id):
    image = Image.query.get(image_id)
    if image is None:
        return jsonify(success=False), 404

    image.liked = True
    db.session.commit()

    return jsonify(success=True), 200


@current_app.route("/unlike-image/<int:image_id>", methods=["POST"])
def unlike_image(image_id):
    image = Image.query.get(image_id)
    if image is None:
        return jsonify(success=False), 404

    image.liked = False
    db.session.commit()

    return jsonify(success=True), 200


@current_app.route("/images-with-likes")
def images_with_likes():
    images = Image.query.filter(Image.liked == True).all()
    return render_template("galerie.html", images=images)
