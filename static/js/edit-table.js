document.addEventListener("DOMContentLoaded", function () {
  // Değişkenler
  const fileName = document
    .getElementById("file_div")
    ?.getAttribute("data-file-name");
  const table = document.getElementById("editable-table");
  const textArea = document.getElementById("editable-content");
  const addRowButton = document.getElementById("add-row-button");
  const deleteRowButton = document.getElementById("delete-row-button");
  const addColumnButton = document.getElementById("add-column-button");
  const deleteColumnButton = document.getElementById("delete-column-button");
  let selectedRow = null;
  let selectedColumn = null;

  function updateDatabase(data) {
    fetch(`/main_page/${fileName}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ updated_data: data }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          console.log("İşlem başarıyla tamamlandı");
        } else {
          console.error("Hata oluştu:", data.message);
        }
      })
      .catch((error) => console.error("AJAX hatası:", error));
  }

  function updateTextContent() {
    const content = textArea.value.trim();

    if (!content) {
      console.warn("Boş içerik gönderilmeye çalışıldı.");
      return;
    }

    const data = [
      {
        update_text: true,
        content: content,
      },
    ];

    updateDatabase(data);
  }

  function updateCell(cell) {
    const rowIndex = cell.getAttribute("data-row");
    const columnName = cell.getAttribute("data-column");
    const newValue = cell.textContent.trim();

    const data = [
      {
        update_cell: true,
        row_index: parseInt(rowIndex),
        column_name: columnName,
        new_value: newValue,
      },
    ];

    console.log("[DEBUG] Gönderilen veri:", JSON.stringify(data, null, 2));
    updateDatabase(data);

    console.log(
      `[DEBUG] Hücre güncellendi: Satır ${rowIndex}, Sütun ${columnName}, Değer: ${newValue}`
    );
  }

  // Hücrelere düzenleme dinleyicisi ekle
  function attachCellListeners() {
    if (!table) {
      return;
    }

    const editableCells = table.querySelectorAll(".editable-cell");

    if (editableCells.length === 0) {
      console.error("[DEBUG] Düzenlenebilir hücre bulunamadı");
      return;
    }

    editableCells.forEach((cell) => {
      cell.addEventListener("blur", function () {
        updateCell(cell);
      });
    });
  }

  function attachTextAreaListener() {
    if (!textArea) {
      console.warn(
        "Metin alanı bulunamadı. attachTextAreaListener çağrılmadı."
      );
      return;
    }

    textArea.addEventListener("blur", function () {
      updateTextContent();
    });
  }

  function addRow() {
    const tbody = table.querySelector("tbody");
    if (!tbody) {
      console.error("[DEBUG] Tablo gövdesi bulunamadı");
      return;
    }

    const newRowIndex = tbody.getElementsByTagName("tr").length;
    const rowTitle = prompt("Lütfen yeni satır için bir başlık girin:");
    if (!rowTitle) {
      alert("Satır başlığı boş bırakılamaz!");
      return;
    }

    const newRow = document.createElement("tr");
    newRow.setAttribute("data-row", newRowIndex);

    const headers = table.querySelectorAll("th");
    const rowData = [];

    headers.forEach((header, index) => {
      const columnName = header.getAttribute("data-column");
      const cell = document.createElement("td");
      cell.setAttribute("contenteditable", "true");
      cell.setAttribute("data-column", columnName);
      cell.setAttribute("data-row", newRowIndex);
      cell.classList.add("editable-cell");

      if (index === 0) {
        cell.textContent = rowTitle;
        rowData.push({ column_name: columnName, value: rowTitle });
      } else {
        cell.textContent = "";
        rowData.push({ column_name: columnName, value: "" });
      }

      newRow.appendChild(cell);
    });

    tbody.appendChild(newRow);

    updateDatabase([
      {
        is_new_row: true,
        row_index: newRowIndex,
        columns: rowData,
      },
    ]);

    attachCellListeners();
  }

  function deleteRow() {
    if (!selectedRow) {
      alert("Lütfen silmek için bir satır seçin");
      return;
    }

    if (
      !confirm("Satır silme işlemi geri alınamaz. Devam etmek istiyor musunuz?")
    ) {
      return;
    }

    const rowIndex = selectedRow.getAttribute("data-row");
    selectedRow.remove();
    selectedRow = null;

    updateDatabase([
      {
        delete_row: true,
        row_index: parseInt(rowIndex),
      },
    ]);
  }

  function addColumn() {
    const newColumnName = prompt("Yeni sütun adını giriniz:");
    if (!newColumnName || newColumnName.trim() === "") {
      return;
    }

    const headerRow = table.querySelector("thead tr");
    const newHeader = document.createElement("th");
    newHeader.setAttribute("contenteditable", "true");
    newHeader.setAttribute("data-column", newColumnName);
    newHeader.textContent = newColumnName;
    headerRow.appendChild(newHeader);

    const rows = table.querySelectorAll("tbody tr");
    rows.forEach((row, rowIndex) => {
      const newCell = document.createElement("td");
      newCell.setAttribute("contenteditable", "true");
      newCell.setAttribute("data-column", newColumnName);
      newCell.setAttribute("data-row", rowIndex);
      newCell.classList.add("editable-cell");
      row.appendChild(newCell);
    });

    updateDatabase([
      {
        add_column: true,
        column_name: newColumnName,
      },
    ]);

    attachCellListeners(); // Yeni hücrelere dinleyici ekle
  }

  function deleteColumn() {
    if (!selectedColumn) {
      alert("Lütfen silmek için bir sütun seçin");
      return;
    }

    if (
      !confirm("Sütun silme işlemi geri alınamaz. Devam etmek istiyor musunuz?")
    ) {
      return;
    }

    table
      .querySelectorAll(`[data-column="${selectedColumn}"]`)
      .forEach((cell) => {
        cell.remove();
      });

    updateDatabase([
      {
        delete_column: true,
        column_name: selectedColumn,
      },
    ]);

    selectedColumn = null;
  }

  // Satır ve sütun seçme
  if (table) {
    table.addEventListener("click", function (e) {
      const row = e.target.closest("tr");
      if (row) {
        if (selectedRow) {
          selectedRow.classList.remove("selected-row");
        }
        selectedRow = row;
        row.classList.add("selected-row");
      }

      const cell = e.target.closest("th, td");
      if (cell) {
        const columnName = cell.getAttribute("data-column");
        if (columnName) {
          if (selectedColumn) {
            table
              .querySelectorAll(`[data-column="${selectedColumn}"]`)
              .forEach((cell) => {
                cell.classList.remove("selected-column");
              });
          }
          selectedColumn = columnName;
          table
            .querySelectorAll(`[data-column="${columnName}"]`)
            .forEach((cell) => {
              cell.classList.add("selected-column");
            });
        }
      }
    });
  }

  // Event listener'lar
  if (addRowButton) addRowButton.addEventListener("click", addRow);
  if (deleteRowButton) deleteRowButton.addEventListener("click", deleteRow);
  if (addColumnButton) addColumnButton.addEventListener("click", addColumn);
  if (deleteColumnButton)
    deleteColumnButton.addEventListener("click", deleteColumn);

  // Başlangıçta tüm hücrelere dinleyici ekle
  attachTextAreaListener();
  attachCellListeners();
});

//Pointer durumunda veri seçme işlemi
document.addEventListener("DOMContentLoaded", function () {
  // Tooltip kutusunu oluştur
  const tooltip = document.createElement("div");
  tooltip.className = "tooltip-box";
  document.body.appendChild(tooltip);

  // Delay ile tablo yüklendikten sonra td'lere ekle (çünkü içerik dynamic)
  setTimeout(() => {
    document.querySelectorAll(".table-responsive td").forEach((td) => {
      td.classList.add("has-tooltip");
      td.setAttribute("data-tooltip", "İşlem için veri seçiniz");
    });

    document.querySelectorAll(".has-tooltip").forEach((el) => {
      el.addEventListener("mouseenter", (e) => {
        tooltip.innerText = el.getAttribute("data-tooltip");
        tooltip.style.display = "block";
      });

      el.addEventListener("mousemove", (e) => {
        tooltip.style.top = `${e.pageY}px`;
        tooltip.style.left = `${e.pageX}px`;
      });

      el.addEventListener("mouseleave", () => {
        tooltip.style.display = "none";
      });
    });
  }, 300); // Tablo yüklenme süresi için küçük bir bekleme süresi
});
