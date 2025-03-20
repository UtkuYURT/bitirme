document.addEventListener("DOMContentLoaded", function () {
  // Tüm seçili hücreleri tutacak ana dizi
  let selectedCells = []; // Seçili hücrelerin DOM referanslarını tutar

  // Tüm td elementlerini seç
  const cells = document.querySelectorAll("td");

  // Tüm tr elementlerini seç (satır başlıkları için)
  const rows = document.querySelectorAll("tr");

  // Tüm sütun başlıklarını seç
  const headers = document.querySelectorAll("th");

  // Satır başlığına tıklama (tüm satırı seçmek veya seçimi kaldırmak için)
  rows.forEach((row) => {
    const firstCell = row.cells[0]; // Satır başlığı (ilk hücre)
    if (firstCell) {
      firstCell.addEventListener("click", function () {
        let isRowSelected = true;

        // Kontrol: Satırdaki tüm hücreler (ilk hücre hariç) seçili mi?
        Array.from(row.cells).forEach((cell, index) => {
          if (index > 0 && !cell.classList.contains("selected")) {
            isRowSelected = false;
          }
        });

        // Eğer satır zaten seçiliyse, seçimi kaldır
        if (isRowSelected) {
          Array.from(row.cells).forEach((cell, index) => {
            if (index > 0) {
              // İlk hücreyi (satır başlığı) hariç tut
              cell.classList.remove("selected");
              selectedCells = selectedCells.filter(
                (selectedCell) => selectedCell !== cell
              );
            }
          });
        } else {
          // Eğer satır seçili değilse, seç
          Array.from(row.cells).forEach((cell, index) => {
            if (index > 0 && !selectedCells.includes(cell)) {
              // İlk hücreyi (satır başlığı) hariç tut
              cell.classList.add("selected");
              selectedCells.push(cell);
            }
          });
        }

        console.log("Tüm seçili hücreler (satır):", selectedCells);
      });
    }
  });

  // Sütun başlığına tıklama (tüm sütunu seçmek veya seçimi kaldırmak için)
  headers.forEach((header, index) => {
    header.addEventListener("click", function () {
      let isColumnSelected = true;

      // Kontrol: Sütundaki tüm hücreler seçili mi?
      rows.forEach((row) => {
        const cell = row.cells[index];
        if (cell && !cell.classList.contains("selected")) {
          isColumnSelected = false;
        }
      });

      // Eğer sütun zaten seçiliyse, seçimi kaldır
      if (isColumnSelected) {
        rows.forEach((row) => {
          const cell = row.cells[index];
          if (cell) {
            cell.classList.remove("selected");
            selectedCells = selectedCells.filter(
              (selectedCell) => selectedCell !== cell
            );
          }
        });
      } else {
        // Eğer sütun seçili değilse, seç
        rows.forEach((row) => {
          const cell = row.cells[index];
          if (cell && !selectedCells.includes(cell)) {
            cell.classList.add("selected");
            selectedCells.push(cell);
          }
        });
      }

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
