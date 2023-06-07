// Fonction pour gérer les erreurs
function handleError(error) {
  console.error("Error:", error);
}

// Fonction pour générer les vignettes
function generateThumbnails(event) {
  event.preventDefault(); // Pour éviter le comportement par défaut du clic sur le lien
  fetch("/admin/generate-thumbnails")
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("Les vignettes ont été générées avec succès !");
      } else {
        alert("Une erreur s'est produite lors de la génération des vignettes.");
      }
    })
    .catch(handleError);
}

// Fonction pour gérer les likes
function handleLike(event) {
  const imageId = event.target.parentElement.getAttribute("data-image-id");
  const isLiked = event.target.textContent.trim().toLowerCase() === "unlike";
  const url = isLiked ? `/unlike-image/${imageId}` : `/like-image/${imageId}`;

  fetch(url, { method: "POST" })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Update the like button text
        event.target.textContent = isLiked ? "Like" : "Unlike";
      } else {
        console.error("Failed to like/unlike image:", data.error);
      }
    })
    .catch(handleError);
}

// Fonction pour gérer les paramètres
function handleParams(event) {
  const imageId = event.target.parentElement.getAttribute("data-image-id");

  // Toggle card-content
  event.target.parentElement
    .querySelector(".card-content")
    .classList.toggle("show");
}

// Fonction pour gérer les suppressions
function handleDelete(event) {
  const imageId = event.target.parentElement.getAttribute("data-image-id");
  fetch(`/delete-image/${imageId}`, { method: "DELETE" })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Optionally remove the image from the UI
        event.target.parentElement.remove();
      } else {
        console.error("Failed to delete image:", data.error);
      }
    })
    .catch(handleError);
}

function loadImage(imageId) {
  const lightbox = document.createElement("div");
  const imageContainer = document.createElement("div");
  const detailsContainer = document.createElement("div");

  lightbox.id = "lightbox";
  imageContainer.id = "image-container";
  detailsContainer.id = "details-container";

  lightbox.appendChild(imageContainer);
  lightbox.appendChild(detailsContainer);
  document.body.appendChild(lightbox);

  fetch(`/galerie/${imageId}`)
    .then((response) => response.json())
    .then((imageData) => {
      lightbox.classList.add("active");
      const img = document.createElement("img");
      const pathParts = imageData.path.split("/");
      const imagePath = pathParts.slice(-2).join("/");

      img.src = `/uploads/${imagePath}`;

      while (imageContainer.firstChild) {
        imageContainer.removeChild(imageContainer.firstChild);
      }
      imageContainer.appendChild(img);

      Object.keys(imageData).forEach((key) => {
        if (key !== "path" && key !== "liked") {
          const detailElement = document.createElement("div");
          detailElement.classList.add("detail");
          detailElement.textContent = `${key}: ${imageData[key]}`;
          detailsContainer.appendChild(detailElement);
        }
      });

      const likeBtn = document.createElement("button");
      likeBtn.classList.add("like-btn");
      likeBtn.setAttribute("data-image-id", imageId);
      likeBtn.textContent = imageData.liked ? "Unlike" : "Like";
      likeBtn.addEventListener("click", handleLike);
      detailsContainer.appendChild(likeBtn);

      const deleteBtn = document.createElement("button");
      deleteBtn.classList.add("delete-btn");
      deleteBtn.setAttribute("data-image-id", imageId);
      deleteBtn.textContent = "Delete";
      deleteBtn.addEventListener("click", handleDelete);
      detailsContainer.appendChild(deleteBtn);
    })
    .catch(handleError);

  lightbox.addEventListener("click", (e) => {
    if (e.target !== e.currentTarget) return;
    lightbox.classList.remove("active");
  });

  // Notez que ce code pour la navigation entre les images n'est pas encore implémenté
  // Vous auriez besoin de mettre en œuvre une logique pour obtenir les ID des images suivante et précédente.
  document.addEventListener("keydown", (e) => {
    if (lightbox.classList.contains("active")) {
      if (e.key === "ArrowRight") {
        // Mettre à jour currentImageId avec l'ID de l'image suivante
        loadImage(currentImageId);
      } else if (e.key === "ArrowLeft") {
        // Mettre à jour currentImageId avec l'ID de l'image précédente
        loadImage(currentImageId);
      } else if (e.key === "Escape") {
        lightbox.classList.remove("active");
      }
    }
  });
}

// Attacher les écouteurs d'événements lorsque le document est chargé
window.addEventListener("DOMContentLoaded", () => {
  // Attacher les écouteurs d'événements
  // document.querySelectorAll(".card img").forEach((image) => {
  //   image.addEventListener("click", (e) => {
  //     loadImage(image.parentElement.getAttribute("data-image-id"));
  //   });
  // });

  document
    .querySelector("#generate-thumbnails-button")
    .addEventListener("click", generateThumbnails);

  document
    .querySelectorAll(".like-btn")
    .forEach((btn) => btn.addEventListener("click", handleLike));

  document
    .querySelectorAll(".delete-btn")
    .forEach((btn) => btn.addEventListener("click", handleDelete));

  document
    .querySelectorAll(".params-btn")
    .forEach((btn) => btn.addEventListener("click", handleParams));
});
