/**
 * Gère les erreurs de requête fetch.
 * @param {Error} error - L'erreur à traiter.
 */
function handleError(error) {
  console.error("Error:", error);
}

/**
 * Génère les vignettes pour toutes les images.
 * @param {Event} event - L'événement de clic.
 */
function generateThumbnails(event) {
  event.preventDefault();

  fetch("/admin/generate-thumbnails")
    .then((response) => response.json())
    .then((data) =>
      alert(
        data.success
          ? "Les vignettes ont été générées avec succès !"
          : "Une erreur s'est produite lors de la génération des vignettes."
      )
    )
    .catch(handleError);
}

/**
 * Met à jour et génère les vignettes pour un répertoire spécifique.
 * @param {Event} event - L'événement de clic.
 */
function handleUpdate(event) {
  event.preventDefault();

  let directoryName = window.location.pathname.includes("galerie")
    ? window.location.pathname.split("/").pop()
    : event.currentTarget.getAttribute("href").split("/").pop();

  const iconElement = event.currentTarget.querySelector("i");
  iconElement.classList.add("rotate");

  fetch(`/admin/generate-thumbnails/${directoryName}`)
    .then((response) => response.json())
    .then((data) => {
      iconElement.classList.remove("rotate");
      alert(
        data.success
          ? "Les vignettes ont été générées avec succès !"
          : "Une erreur s'est produite lors de la génération des vignettes."
      );
      if (window.location.pathname.includes("galerie")) location.reload();
    })
    .catch((error) => {
      iconElement.classList.remove("rotate");
      handleError(error);
    });
}

/**
 * Like ou Unlike une image spécifique.
 * @param {Event} event - L'événement de clic.
 */
function handleLike(event) {
  let imageId = window.location.pathname.includes("/image/")
    ? window.location.pathname.split("/").pop()
    : event.target.parentElement.getAttribute("data-image-id");
  const isLiked = event.target.textContent.trim().toLowerCase() === "unlike";
  const url = isLiked ? `/unlike-image/${imageId}` : `/like-image/${imageId}`;

  fetch(url, { method: "POST" })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) event.target.textContent = isLiked ? "Like" : "Unlike";
      else console.error("Failed to like/unlike image:", data.error);
    })
    .catch(handleError);
}

/**
 * Affiche ou masque le contenu de la carte.
 * @param {Event} event - L'événement de clic.
 */
function handleParams(event) {
  event.target.parentElement
    .querySelector(".card-content")
    .classList.toggle("show");
}

/**
 * Supprime une image spécifique.
 * @param {Event} event - L'événement de clic.
 */
function handleDelete(event) {
  let imageId = window.location.pathname.includes("image")
    ? window.location.pathname.split("/").pop()
    : event.target.parentElement.getAttribute("data-image-id");

  fetch(`/delete-image/${imageId}`, { method: "DELETE" })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        if (window.location.pathname.includes("image")) {
          window.location.href = `${window.location
            .toString()
            .slice(0, window.location.toString().lastIndexOf("/"))}/${
            data.next_image
          }`;
        } else {
          event.target.parentElement.remove();
        }
      } else console.error("Failed to delete image:", data.error);
    })
    .catch(handleError);
}

/**
 * Fait défiler la page vers le haut.
 */
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/**
 * Vérifie si le scroll dépasse une certaine position pour afficher ou masquer le bouton de retour en haut.
 */
function checkScroll() {
  document.querySelector("#back-to-top").style.display =
    window.scrollY > 300 ? "flex" : "none";
}

// Attache les écouteurs d'événements lorsque le document est chargé
window.addEventListener("DOMContentLoaded", () => {
  if (window.location.pathname.includes("admin")) {
    document
      .querySelector("#generate-thumbnails-button")
      .addEventListener("click", generateThumbnails);
  }

  document
    .querySelectorAll(".directory__update")
    .forEach((btn) => btn.addEventListener("click", handleUpdate));
  document
    .querySelectorAll(".title-bar__update")
    .forEach((btn) => btn.addEventListener("click", handleUpdate));
  document
    .querySelectorAll(".like-btn")
    .forEach((btn) => btn.addEventListener("click", handleLike));
  document
    .querySelectorAll(".delete-btn")
    .forEach((btn) => btn.addEventListener("click", handleDelete));
  document
    .querySelectorAll(".params-btn")
    .forEach((btn) => btn.addEventListener("click", handleParams));

  document.querySelector("#back-to-top").addEventListener("click", scrollToTop);
  window.addEventListener("scroll", checkScroll);
});
