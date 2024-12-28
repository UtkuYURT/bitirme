document.addEventListener("DOMContentLoaded", function () {
  // Tabloyu seç
  const table = document.querySelector(".table-responsive table");

  if (table) {
    // Tablo hücrelerini düzenlenebilir hale getir
    table.querySelectorAll("td").forEach((cell) => {
      cell.addEventListener("dblclick", function () {
        // Eski değeri kaydet
        const oldValue = cell.textContent;

        // Düzenlenebilir bir input oluştur
        const input = document.createElement("input");
        input.type = "text";
        input.value = oldValue;
        input.classList.add("form-control");

        // Hücreyi temizle ve input ekle
        cell.textContent = "";
        cell.appendChild(input);

        // Input'tan çıkıldığında yeni değeri kaydet
        input.addEventListener("blur", function () {
          const newValue = input.value;
          cell.textContent = newValue; // Hücreyi güncelle
        });

        // Enter tuşuna basıldığında değeri kaydet
        input.addEventListener("keydown", function (e) {
          if (e.key === "Enter") {
            input.blur();
          }
        });

        // Otomatik olarak input'a odaklan
        input.focus();
      });
    });
  } else {
    console.error("Tablo bulunamadı.");
  }
});
