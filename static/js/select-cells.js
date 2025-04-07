document.addEventListener("DOMContentLoaded", function () {
  // Tüm seçili hücreleri tutacak dizi
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
        // (satır başlığı) hariç tut
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
    rows.forEach((row, rowIndex) => {
      if (rowIndex === 0) return;
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

        toggleRowSelection(row, !isRowSelected);
        console.log("[DEBUG] Tüm seçili hücreler (satır):", selectedCells);
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

      toggleColumnSelection(index, !isColumnSelected);
      console.log("[DEBUG] Tüm seçili hücreler (sütun):", selectedCells);
    });
  });

  // Hücre seçimi
  cells.forEach((cell) => {
    cell.addEventListener("click", function () {
      // Satır başlığını (row[0]) kontrol et ve hariç tut
      const parentRow = cell.parentElement; // Hücrenin ait olduğu satırı al
      if (parentRow && parentRow.cells[0] === cell) {
        // Tıklanan hücre satır başlığıysa, hiçbir şey yapma
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

      console.log("[DEBUG] Tüm seçili hücreler:", selectedCells);
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
    console.log("[DEBUG] Seçimler temizlendi");
  });

  /**
   * Flask'a seçili hücreleri ve işlem türünü gönderir.
   * @param {string} operation - İşlem türü (örneğin, "arithmetic").
   */
  function calculate(operation) {
    if (selectedCells.length === 0) {
      alert("Lütfen önce hücreleri seçin.");
      return;
    }

    if (operation === "regression") {
      // Sütunlara göre gruplandır
      const columnGroups = selectedCells.reduce((acc, cell) => {
        const columnIndex = cell.cellIndex; // Hücrenin sütun indeksini al

        // Sütun gruplarını oluştur
        if (!acc[columnIndex]) acc[columnIndex] = [];
        acc[columnIndex].push(parseFloat(cell.textContent.trim())); // Hücre değerini ekle
        return acc;
      }, {});

      console.log("[DEBUG] Sütun grupları (columnGroups):", columnGroups);

      const columns = Object.keys(columnGroups);
      if (columns.length < 2) {
        alert("Regresyon testi için en az iki sütun seçmelisiniz.");
        return;
      }

      // Sütun gruplarını iki boyutlu bir diziye dönüştür
      const regressionValues = columns.map((col) => columnGroups[col]);

      console.log(
        "[DEBUG] Backend'e gönderilecek regressionValues:",
        regressionValues
      );

      fetch("/mathematical_operations", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          selectedValues: regressionValues,
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
          console.error("[DEBUG] Veri gönderilirken hata oluştu:", error);
        });

      return;
    }

    const selectedValues = selectedCells.map((cell) => cell.textContent.trim());
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
        console.error("[DEBUG] Veri gönderilirken hata oluştu:", error);
      });
  }

  const operationButtons = [
    { id: "calculate-average", operation: "arithmetic" },
    { id: "calculate-geometric", operation: "geometric" },
    { id: "calculate-harmonic", operation: "harmonic" },
    { id: "calculate-median", operation: "median" },
    { id: "calculate-correlation", operation: "correlation" },
    { id: "calculate-std-dev", operation: "std_dev" },
    { id: "calculate-variance", operation: "variance" },
    { id: "calculate-z-test", operation: "z_test" },
    { id: "calculate-t-test", operation: "t_test" },
    { id: "calculate-regression", operation: "regression" },
    { id: "calculate-frequency", operation: "frequency" },
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
