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

// Attacher les écouteurs d'événements lorsque le document est chargé
window.addEventListener("DOMContentLoaded", () => {
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
