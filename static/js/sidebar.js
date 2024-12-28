// çıkış yap
const logOut = document.querySelector("#logout-button");
logOut?.addEventListener("click", () => {
  window.location.href = "/";
  alert("Çıkış Yapıldı");
});

// bir alt işlemdeyken başka birine tıklayınca onu kapat (sidebar içinde)
document.addEventListener("DOMContentLoaded", () => {
  const toggleButtons = document.querySelectorAll(".toggle-button");

  function closeAllButtonsExcept(currentButton) {
    toggleButtons.forEach((button) => {
      if (
        button !== currentButton &&
        button.getAttribute("aria-expanded") === "true"
      ) {
        const icon = button.querySelector(".toggle-icon");
        const collapseElement = document.querySelector(
          button.getAttribute("data-bs-target")
        );

        button.setAttribute("aria-expanded", "false");
        button.classList.remove("collapsed");
        if (collapseElement) {
          collapseElement.classList.remove("show");
          icon.classList.remove("fa-chevron-right");
          icon.classList.add("fa-chevron-down");
        }
      }
    });
  }

  toggleButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const isCurrentlyExpanded =
        button.getAttribute("aria-expanded") == "true";

      const icon = button.querySelector(".toggle-icon");
      closeAllButtonsExcept(button);

      if (isCurrentlyExpanded) {
        button.setAttribute("aria-expanded", "true");
        button.classList.add("collapsed");
        icon.classList.remove("fa-chevron-down");
        icon.classList.add("fa-chevron-right");
      } else {
        button.setAttribute("aria-expanded", "false");
        button.classList.remove("collapsed");
        icon.classList.remove("fa-chevron-right");
        icon.classList.add("fa-chevron-down");
      }
    });
  });
});

// Sidebar kapa aç
document.addEventListener("DOMContentLoaded", function () {
  // Her sidebar-control elementini seç
  document.querySelectorAll("#sidebar-control").forEach((control) => {
    control.addEventListener("click", function (e) {
      e.preventDefault(); // Link davranışını engelle

      // En yakın sidebar elementini bul
      const parentSidebar = this.closest("[id^='sidebar-']");
      if (parentSidebar) {
        parentSidebar.classList.toggle("close");
      }
    });
  });
});
