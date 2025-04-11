// çıkış yap
const logOut = document.querySelector("#logout-button");
if (logOut) {
  logOut.addEventListener("click", () => {
    window.location.href = "/";
    alert("Çıkış Yapıldı");
  });
}

// Sidebar açma kapama işlemi
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".sidebar-control").forEach((control) => {
    control.addEventListener("click", function (e) {
      e.preventDefault();

      // En yakın sidebar elementini bul
      const parentSidebar = this.closest("[id^='sidebar-']");
      if (parentSidebar) {
        parentSidebar.classList.toggle("close");
      }

      // Sidebar toggle edildikten sonra margin kontrolü
      setTimeout(updateBodyMarginForSidebar, 300);
    });
  });

  // Sayfa boyutu 768px altına düştüğünde sidebar'ı kapat, 768px üstüne çıkınca aç
  function checkScreenSize() {
    const sidebar = document.querySelector("[id^='sidebar-']");
    if (window.innerWidth <= 768) {
      if (sidebar && !sidebar.classList.contains("close")) {
        sidebar.classList.add("close");
      }
    } else {
      if (sidebar && sidebar.classList.contains("close")) {
        sidebar.classList.remove("close");
      }
    }
    updateBodyMarginForSidebar();
  }

  checkScreenSize();
  window.addEventListener("resize", checkScreenSize);
});

// Sidebar içindeki toggle butonları işlemi
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
        }
        if (icon) {
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
        if (icon) {
          icon.classList.remove("fa-chevron-down");
          icon.classList.add("fa-chevron-right");
        }
      } else {
        button.setAttribute("aria-expanded", "false");
        button.classList.remove("collapsed");
        if (icon) {
          icon.classList.remove("fa-chevron-right");
          icon.classList.add("fa-chevron-down");
        }
      }
    });
  });
});

// Sidebar dışında bir yere tıklayınca sidebar'ı kapat
document.addEventListener("click", function (e) {
  const sidebar = document.querySelector("[id^='sidebar-']");
  const sidebarControl = document.querySelector(".sidebar-control");

  if (
    sidebar &&
    !sidebar.contains(e.target) &&
    !sidebarControl.contains(e.target)
  ) {
    sidebar.classList.add("close");
    updateBodyMarginForSidebar();
  }
});

// ✅ Sidebar açıkken 768-992px arasında body margin-left: 20vw yap
function updateBodyMarginForSidebar() {
  const sidebar = document.querySelector("[id^='sidebar-']");
  const body = document.body;

  const isSidebarOpen = sidebar && !sidebar.classList.contains("close");
  const width = window.innerWidth;

  if (isSidebarOpen && width >= 768) {
    body.style.marginLeft = "140px";
  } else {
    body.style.marginLeft = "";
  }
}
