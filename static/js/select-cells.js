document.addEventListener("DOMContentLoaded", function () {
  // Tüm seçili hücreleri tutacak ana dizi
  let selectedCells = [];

  const cells = document.querySelectorAll("td");

  const rows = document.querySelectorAll("tr");

  const headers = document.querySelectorAll("th");

  /**
   * Satırdaki hücrelerin seçimini değiştirir.
   * @param {HTMLTableRowElement} row - İşlem yapılacak satır.
   * @param {boolean} select - Seçim durumu (true: seç, false: kaldır).
   */
  function toggleRowSelection(row, select) {
    Array.from(row.cells).forEach((cell, index) => {
      if (index > 0) {
        // İlk hücreyi (satır başlığı) hariç tut
        if (select) {
          if (!selectedCells.includes(cell)) {
            cell.classList.add("selected");
            selectedCells.push(cell);
          }
        } else {
          cell.classList.remove("selected");
          selectedCells = selectedCells.filter(
            (selectedCell) => selectedCell !== cell
          );
        }
      }
    });
  }

  /**
   * Sütundaki hücrelerin seçimini değiştirir.
   * @param {number} columnIndex - İşlem yapılacak sütunun indeksi.
   * @param {boolean} select - Seçim durumu (true: seç, false: kaldır).
   */
  function toggleColumnSelection(columnIndex, select) {
    rows.forEach((row) => {
      const cell = row.cells[columnIndex];
      if (cell) {
        if (select) {
          if (!selectedCells.includes(cell)) {
            cell.classList.add("selected");
            selectedCells.push(cell);
          }
        } else {
          cell.classList.remove("selected");
          selectedCells = selectedCells.filter(
            (selectedCell) => selectedCell !== cell
          );
        }
      }
    });
  }

  // Satır başlığına tıklama (tüm satırı seçmek veya seçimi kaldırmak için)
  rows.forEach((row) => {
    const firstCell = row.cells[0]; // Satır başlığı (ilk hücre)
    if (firstCell) {
      firstCell.addEventListener("click", function () {
        const isRowSelected = Array.from(row.cells).every(
          (cell, index) => index === 0 || cell.classList.contains("selected")
        );

        toggleRowSelection(row, !isRowSelected); // Seçimi tersine çevir
        console.log("Tüm seçili hücreler (satır):", selectedCells);
      });
    }
  });

  // Sütun başlığına tıklama (tüm sütunu seçmek veya seçimi kaldırmak için)
  headers.forEach((header, index) => {
    header.addEventListener("click", function () {
      const isColumnSelected = Array.from(rows).every((row) => {
        const cell = row.cells[index];
        return cell && cell.classList.contains("selected");
      });

      toggleColumnSelection(index, !isColumnSelected); // Seçimi tersine çevir
      console.log("Tüm seçili hücreler (sütun):", selectedCells);
    });
  });

  // Hücre seçimi için kod
  cells.forEach((cell) => {
    cell.addEventListener("click", function () {
      // Satır başlığını (row[0]) kontrol et ve hariç tut
      const parentRow = cell.parentElement; // Hücrenin ait olduğu satırı al
      if (parentRow && parentRow.cells[0] === cell) {
        // Eğer tıklanan hücre satır başlığıysa, hiçbir şey yapma
        return;
      }

      const isSelected = selectedCells.includes(cell);

      if (isSelected) {
        // Seçili ise, seçimi kaldır
        cell.classList.remove("selected");
        selectedCells = selectedCells.filter(
          (selectedCell) => selectedCell !== cell
        );
      } else {
        // Seçili değilse, seç
        cell.classList.add("selected");
        selectedCells.push(cell);
      }

      console.log("Tüm seçili hücreler:", selectedCells);
    });
  });

  // Temizleme butonu için kod
  const clearButton = document.getElementById("clear-button");
  clearButton.addEventListener("click", function (e) {
    e.preventDefault(); // Link tıklamasını engelle
    selectedCells.forEach((cell) => {
      cell.classList.remove("selected");
    });
    selectedCells = []; // Diziyi temizle
    console.log("Seçimler temizlendi");
  });
});
