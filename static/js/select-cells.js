document.addEventListener("DOMContentLoaded", function () {
  // Tüm seçili değerleri tutacak ana dizi
  let selectedValues = [];

  // Tüm th elementlerini seç (sütun başlıkları için)
  const headers = document.querySelectorAll("th");

  // Tüm td elementlerini seç
  const cells = document.querySelectorAll("td");

  // Sütun seçimi için kod
  headers.forEach((header, index) => {
    header.addEventListener("click", function () {
      const allRows = document.querySelectorAll("tr");

      allRows.forEach((row, rowIndex) => {
        if (rowIndex === 0) return;

        const cell = row.cells[index];
        if (cell) {
          const value = cell.textContent.trim();
          if (!selectedValues.includes(value)) {
            selectedValues.push(value);
            cell.classList.add("selected");
          }
        }
      });

      console.log("Tüm seçili değerler:", selectedValues);
    });
  });

  // Hücre seçimi için kod
  cells.forEach((cell) => {
    cell.addEventListener("click", function () {
      const cellIndex = this.cellIndex;
      const value = this.textContent.trim();

      if (cellIndex === 0) {
        // Satır başı tıklaması - sadece seç
        const row = this.parentElement;
        const rowCells = row.querySelectorAll("td");

        rowCells.forEach((cell, index) => {
          if (index !== 0) {
            const value = cell.textContent.trim();
            if (!selectedValues.includes(value)) {
              selectedValues.push(value);
              cell.classList.add("selected");
            }
          }
        });
      } else {
        // Tekli hücre tıklaması - toggle davranışı
        const isSelected = selectedValues.includes(value);

        if (isSelected) {
          // Seçili ise, seçimi kaldır
          selectedValues = selectedValues.filter((v) => v !== value);
          this.classList.remove("selected");
        } else {
          // Seçili değilse, seç
          selectedValues.push(value);
          this.classList.add("selected");
        }
      }

      console.log("Tüm seçili değerler:", selectedValues);
    });
  });

  // Temizleme butonu için yeni kod
  const clearButton = document.getElementById("clear-button");
  clearButton.addEventListener("click", function (e) {
    e.preventDefault(); // Link tıklamasını engelle
    selectedValues = []; // Diziyi temizle
    const selectedCells = document.querySelectorAll(".selected");
    selectedCells.forEach((cell) => {
      cell.classList.remove("selected");
    });
    console.log("Seçimler temizlendi");
  });
});
