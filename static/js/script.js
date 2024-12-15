const alerts = document.querySelectorAll(".alert-dismissible");

alerts.forEach((alert) => {
  setTimeout(() => {
    alert.classList.add("fade");
    setTimeout(() => alert.remove(), 500);
  }, 2000);
});
