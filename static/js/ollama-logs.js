document.addEventListener("DOMContentLoaded", function () {
  const rows = document.querySelectorAll(".log-row");
  const soruSpan = document.getElementById("modalSoru");
  const cevapSpan = document.getElementById("modalCevap");
  const fotoDiv = document.getElementById("modalFotoDiv");
  const logModal = document.getElementById("logModal");

  if (!rows.length || !soruSpan || !cevapSpan || !fotoDiv || !logModal) return;

  const modalInstance = new bootstrap.Modal(logModal);

  rows.forEach(function (row) {
    row.addEventListener("click", function () {
      const soru = this.dataset.soru;
      const cevap = this.dataset.cevap;
      const foto = this.dataset.foto;

      soruSpan.textContent = soru;
      cevapSpan.textContent = cevap;

      if (foto) {
        fotoDiv.innerHTML = `<img src="data:image/png;base64,${foto}" alt="Fotoğraf" style="max-width:100%;height:auto;" />`;
      }

      modalInstance.show();
    });
  });
});
