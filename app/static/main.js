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
  let btn = event.currentTarget;

  let imageId = window.location.pathname.includes("/image/")
    ? window.location.pathname.split("/").pop()
    : btn.getAttribute("data-image-id");

  const isLiked = btn.classList.contains("liked");

  const url = isLiked ? `/unlike-image/${imageId}` : `/like-image/${imageId}`;

  fetch(url, { method: "POST" })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Modifie la classe du bouton et l'icône en fonction de si l'image est aimée ou non
        if (isLiked) {
          btn.classList.remove("liked");
          btn.innerHTML = "<i class='far fa-heart'></i>";
        } else {
          btn.classList.add("liked");
          btn.innerHTML = "<i class='fas fa-heart'></i>";
        }
      } else {
        console.error("Failed to like/unlike image:", data.error);
      }
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

function copyToClipboard(element) {
  // Créer un champ de saisie temporaire
  const tempInput = document.createElement("input");
  // Définir sa valeur sur le texte de l'élément cible
  tempInput.value = element.textContent;
  // Ajouter l'élément au corps du document
  document.body.appendChild(tempInput);
  // Sélectionner le texte du champ de saisie
  tempInput.select();
  // Copier le texte sélectionné
  document.execCommand("copy");
  // Supprimer l'élément temporaire du corps du document
  document.body.removeChild(tempInput);

  // Affiche une indication que le texte a été copié
  const copyIndicator = document.createElement("span");
  copyIndicator.textContent = "Copié !";
  copyIndicator.classList.add("copy-indicator");
  element.appendChild(copyIndicator);

  // Fait disparaître l'indicateur après 2 secondes
  setTimeout(() => {
    element.removeChild(copyIndicator);
  }, 2000);
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

  document.querySelectorAll(".image-info-item__content").forEach((element) => {
    element.addEventListener("click", () => copyToClipboard(element));
  });

  document.querySelector("#back-to-top").addEventListener("click", scrollToTop);
  window.addEventListener("scroll", checkScroll);

  document.addEventListener("keydown", function (event) {
    const key = event.key; // "ArrowRight", "ArrowLeft", "ArrowUp", "ArrowDown", "Delete"

    if (window.location.pathname.includes("/image/")) {
      if (key === "ArrowLeft") {
        const prevBtn = document.getElementById("prev-btn");
        if (prevBtn) {
          window.location.href = prevBtn.href;
        }
      } else if (key === "ArrowRight") {
        const nextBtn = document.getElementById("next-btn");
        if (nextBtn) {
          window.location.href = nextBtn.href;
        }
      } else if (key === "Delete") {
        const deleteBtn = document.getElementById("delete-btn");
        if (deleteBtn) {
          deleteBtn.click();
        }
      }
    }
  });
});
