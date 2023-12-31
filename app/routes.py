import os

from flask import (
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from sqlalchemy import and_, asc, desc, func

from app import db
from app.models import Image
from app.utils import create_image_record, get_directory_list, get_ordered_images


@current_app.route("/")
def index():
    """
    Page d'accueil. Affiche une liste des répertoires disponibles.
    """
    directories = get_directory_list()
    return render_template("index.html", directories=directories)


@current_app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """
    Retourne un fichier du répertoire de téléchargement.
    """
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@current_app.route("/galerie")
@current_app.route("/galerie/")
def images():
    """
    Galerie d'images. Les images peuvent être triées.
    """
    likes = request.args.get("likes", type=lambda v: v.lower() == "true", default=None)
    order_type = request.args.get("order_type", "default")

    query = Image.query
    if likes is not None:
        query = query.filter(Image.liked == likes)

    images = get_ordered_images(query, order_type)
    return render_template(
        "galerie.html", images=images, likes=likes, directory="Toutes les images"
    )


@current_app.route("/galerie/<path:directory>")
def galerie(directory):
    """
    Galerie d'images pour un répertoire spécifique. Les images peuvent être triées.
    """
    likes = request.args.get("likes", type=lambda v: v.lower() == "true", default=None)
    order_type = request.args.get("order_type", "default")

    query = Image.query.filter(Image.path.startswith(directory))
    if likes is not None:
        query = query.filter(Image.liked == likes)

    images = get_ordered_images(query, order_type)
    return render_template(
        "galerie.html", images=images, likes=likes, directory=directory
    )


@current_app.route("/search")
def search_images():
    """
    Recherche d'images par mots clés dans les paramètres.
    """
    likes = request.args.get("likes", type=lambda v: v.lower() == "true", default=None)
    search_query = request.args.get("q", "")
    keywords = search_query.split()
    conditions = [
        func.lower(Image.parameters).contains(func.lower(keyword))
        for keyword in keywords
    ]

    order_type = request.args.get("order_type", "default")
    query = Image.query.filter(and_(*conditions))
    if likes is not None:
        query = query.filter(Image.liked == likes)

    images = get_ordered_images(query, order_type)

    return render_template(
        "galerie.html",
        images=images,
        likes=likes,
        directory="Recherche",
        search_query=search_query,
    )


@current_app.route("/image/<int:image_id>")
def image_detail(image_id):
    """
    Récupère le détail d'une image spécifique par son ID.
    Possibilité de retourner les détails en format JSON.
    """
    likes = request.args.get("likes", type=lambda v: v.lower() == "true", default=None)
    json_output = request.args.get(
        "json", default=False, type=lambda v: v.lower() == "true"
    )
    current_image = Image.query.get(image_id)
    if current_image:
        if json_output:
            current_image = current_image.__dict__
            current_image.pop(
                "_sa_instance_state", None
            )  # Supprimer l'attribut interne indésirable

            return jsonify(current_image), 200
        else:
            return render_template("image.html", image=current_image, likes=likes)
    else:
        return jsonify(error="Image not found"), 404


@current_app.route("/image/<int:image_id>/next")
def next_image(image_id):
    """
    Redirige vers l'image suivante dans la liste basée sur l'ID de l'image actuelle.
    """
    likes = request.args.get("likes", type=lambda v: v.lower() == "true", default=None)

    current_image = Image.query.get(image_id)
    if not current_image:
        return jsonify(error="Image not found"), 404

    query = Image.query.filter(Image.path > current_image.path)
    if likes is not None:
        query = query.filter(Image.liked == likes)

    next_image = query.order_by(Image.path).first()

    if next_image:
        return redirect(url_for("image_detail", image_id=next_image.id, likes=likes))
    else:
        return redirect(url_for("image_detail", image_id=current_image.id))


@current_app.route("/image/<int:image_id>/prev")
def prev_image(image_id):
    """
    Redirige vers l'image précédente dans la liste basée sur l'ID de l'image actuelle.
    """
    likes = request.args.get("likes", type=lambda v: v.lower() == "true", default=None)

    current_image = Image.query.get(image_id)
    if not current_image:
        return jsonify(error="Image not found"), 404

    query = Image.query.filter(Image.path < current_image.path)
    if likes is not None:
        query = query.filter(Image.liked == likes)

    prev_image = query.order_by(Image.path.desc()).first()

    if prev_image:
        return redirect(url_for("image_detail", image_id=prev_image.id, likes=likes))
    else:
        return redirect(url_for("image_detail", image_id=current_image.id))


@current_app.route("/delete-image/<int:image_id>", methods=["DELETE"])
def delete_image(image_id):
    """
    Supprime une image spécifique par son ID.
    Supprime également sa vignette associée.
    """
    image = Image.query.get(image_id)
    if image is None:
        return jsonify(success=False), 404

    try:
        image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], image.path)
        os.remove(image_path)  # delete original image
        os.remove(
            os.path.join(current_app.static_folder, image.thumbnail)
        )  # delete thumbnail
    except Exception as e:
        # return jsonify(success=False, error=str(e)), 500
        print(str(e))

    next_image = (
        Image.query.filter(Image.path > image.path).order_by(Image.path).first()
    )
    db.session.delete(image)
    db.session.commit()

    return jsonify(success=True, next_image=next_image.id), 200


@current_app.route("/like-image/<int:image_id>", methods=["POST"])
def like_image(image_id):
    """
    Ajoute un "j'aime" à une image spécifique par son ID.
    """
    image = Image.query.get(image_id)
    if image is None:
        return jsonify(success=False), 404

    image.liked = True
    db.session.commit()

    return jsonify(success=True), 200


@current_app.route("/unlike-image/<int:image_id>", methods=["POST"])
def unlike_image(image_id):
    """
    Supprime un "j'aime" d'une image spécifique par son ID.
    """
    image = Image.query.get(image_id)
    if image is None:
        return jsonify(success=False), 404

    image.liked = False
    db.session.commit()

    return jsonify(success=True), 200


@current_app.route("/admin")
def administration():
    """
    Page d'administration. Permet de générer des vignettes et d'uploader de nouvelles images.
    """
    return render_template(
        "admin.html", uploaded_folder=current_app.config["UPLOAD_FOLDER"]
    )


@current_app.route("/admin/generate-thumbnails", defaults={"directory": None})
@current_app.route("/admin/generate-thumbnails/<path:directory>")
def generate_thumbnails(directory):
    """
    Génère des vignettes pour toutes les images dans le répertoire spécifié.
    Si aucun répertoire n'est spécifié, les vignettes sont générées pour toutes les images.
    """
    directories = [directory] if directory else get_directory_list()
    for directory in directories:
        basepath = os.path.join(current_app.config["UPLOAD_FOLDER"], directory)
        for filename in os.listdir(basepath):
            image_path = os.path.join(basepath, filename)
            # Check if the image already exists in the database
            image = Image.query.filter_by(
                path=image_path.replace(current_app.config["UPLOAD_FOLDER"], "")
            ).first()
            if not image and os.path.isfile(image_path):
                image = create_image_record(image_path, directory)
                if image:
                    db.session.add(image)
    db.session.commit()
    return jsonify(success=True), 200
