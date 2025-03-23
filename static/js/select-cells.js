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

  /**
   * Flask'a seçili hücreleri ve işlem türünü gönderir.
   * @param {string} operation - İşlem türü (örneğin, "arithmetic").
   */
  function calculate(operation) {
    const selectedValues = selectedCells.map((cell) => cell.textContent.trim());

    if (selectedValues.length === 0) {
      alert("Lütfen önce hücreleri seçin.");
      return;
    }

    fetch("/mathematical_operations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        selectedValues: selectedValues,
        operation: operation,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Sunucudan hata geldi: " + response.statusText);
        }
        return response.json();
      })
      .then((data) => {
        if (data.redirect_url) {
          window.location.href = data.redirect_url;
        }
      })
      .catch((error) => {
        console.error("Veri gönderilirken hata oluştu:", error);
      });
  }

  const operationButtons = [
    { id: "calculate-average", operation: "arithmetic" },
    { id: "calculate-geometric", operation: "geometric" },
    { id: "calculate-harmonic", operation: "harmonic" },
    { id: "calculate-median", operation: "median" },
  ];

  operationButtons.forEach(({ id, operation }) => {
    const button = document.getElementById(id);
    if (button)
      button.addEventListener("click", (e) => {
        e.preventDefault();
        calculate(operation);
      });
  });
});
