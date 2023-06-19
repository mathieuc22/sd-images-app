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

function handleUpdate(event) {
  event.preventDefault(); // Pour éviter le comportement par défaut du clic sur le lien
  let directoryName;
  if (window.location.pathname.includes("galerie")) {
    directoryName = window.location.pathname.split("/").pop();
  } else {
    directoryName = event.currentTarget.getAttribute("href").split("/").pop();
  }

  // Trouver l'élément icône et ajouter la classe 'rotate'
  const iconElement = event.currentTarget.querySelector("i");
  iconElement.classList.add("rotate");

  fetch(`/admin/generate-thumbnails/${directoryName}`)
    .then((response) => response.json())
    .then((data) => {
      // Enlever la classe 'rotate' une fois la requête finie
      iconElement.classList.remove("rotate");

      if (data.success) {
        alert("Les vignettes ont été générées avec succès !");
      } else {
        alert("Une erreur s'est produite lors de la génération des vignettes.");
      }

      if (window.location.pathname.includes("galerie")) {
        location.reload();
      }
    })
    .catch((error) => {
      // Enlever la classe 'rotate' même si une erreur s'est produite
      iconElement.classList.remove("rotate");
      handleError(error);
    });
}

// Fonction pour gérer les likes
function handleLike(event) {
  let imageId;
  if (window.location.pathname.includes("image")) {
    imageId = window.location.pathname.split("/").pop();
  } else {
    imageId = event.target.parentElement.getAttribute("data-image-id");
  }
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
  // Toggle card-content
  event.target.parentElement
    .querySelector(".card-content")
    .classList.toggle("show");
}

// Fonction pour gérer les suppressions
function handleDelete(event) {
  let imageId;
  if (window.location.pathname.includes("image")) {
    imageId = window.location.pathname.split("/").pop();
  } else {
    imageId = event.target.parentElement.getAttribute("data-image-id");
  }
  fetch(`/delete-image/${imageId}`, { method: "DELETE" })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Optionally remove the image from the UI
        if (window.location.pathname.includes("image")) {
          // window.location = document.referrer;
          window.location =
            window.location
              .toString()
              .slice(0, window.location.toString().lastIndexOf("/")) +
            "/" +
            data.next_image;
        } else {
          event.target.parentElement.remove();
        }
      } else {
        console.error("Failed to delete image:", data.error);
      }
    })
    .catch(handleError);
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function checkScroll() {
  if (window.scrollY > 300) {
    document.querySelector("#back-to-top").style.display = "flex";
  } else {
    document.querySelector("#back-to-top").style.display = "none";
  }
}

// Attacher les écouteurs d'événements lorsque le document est chargé
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
    .querySelectorAll(".update")
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
