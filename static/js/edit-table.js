document.addEventListener("DOMContentLoaded", function () {
  // Genel değişkenler
  const fileName = document
    .getElementById("file_div")
    ?.getAttribute("data-file-name");
  const table = document.getElementById("editable-table");
  const addRowButton = document.getElementById("add-row-button");
  const deleteRowButton = document.getElementById("delete-row-button");
  const addColumnButton = document.getElementById("add-column-button");
  const deleteColumnButton = document.getElementById("delete-column-button");
  let selectedRow = null;
  let selectedColumn = null;

  // Veritabanını güncelleme fonksiyonu
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
  
  // Hücre güncelleme fonksiyonu
  function updateCell(cell) {
    const rowIndex = cell.getAttribute("data-row");
    const columnName = cell.getAttribute("data-column");
    const newValue = cell.textContent.trim();

    const data = [
      {
        update_cell: true,
        row_index: parseInt(rowIndex),
        column_name: columnName,
        new_value: newValue, // 'value' yerine 'new_value' kullanıldı
      },
    ];

    console.log("Gönderilen veri:", JSON.stringify(data, null, 2)); // Veriyi kontrol et
    updateDatabase(data);

    console.log(
      `Hücre güncellendi: Satır ${rowIndex}, Sütun ${columnName}, Değer: ${newValue}`
    );
  }

  // Hücrelere düzenleme olay dinleyicisi ekleme
  function attachCellListeners() {
    const editableCells = table.querySelectorAll(".editable-cell");
    editableCells.forEach((cell) => {
      cell.addEventListener("blur", function () {
        updateCell(cell); // Hücre düzenlemesi tamamlandığında güncelle
      });
    });
  }

  // Satır ekleme fonksiyonu
  function addRow() {
    const tbody = table.querySelector("tbody");
    if (!tbody) {
      console.error("Tablo gövdesi bulunamadı");
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

    attachCellListeners(); // Yeni hücrelere olay dinleyicisi ekle
  }

  // Satır silme fonksiyonu
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

  // Sütun ekleme fonksiyonu
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

    attachCellListeners(); // Yeni hücrelere olay dinleyicisi ekle
  }

  // Sütun silme fonksiyonu
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

  // Satır ve sütun seçme işlemleri
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

  // Başlangıçta tüm hücrelere olay dinleyicisi ekle
  attachCellListeners();
});
