document.addEventListener("DOMContentLoaded", function () {
  const fileName = document
    .getElementById("file_div")
    .getAttribute("data-file-name");
  const table = document.getElementById("editable-table");

  // Satır ekleme fonksiyonu
  document.getElementById("addRowBtn").addEventListener("click", function() {
    const tbody = table.querySelector("tbody");
    const newRow = document.createElement("tr");
    const columns = table.querySelectorAll("thead th");
    const newRowIndex = tbody.children.length;
    
    newRow.setAttribute("data-row", newRowIndex);
    
    columns.forEach(column => {
      const td = document.createElement("td");
      td.setAttribute("contenteditable", "true");
      td.setAttribute("data-column", column.getAttribute("data-column"));
      td.setAttribute("data-row", newRowIndex);
      td.classList.add("editable-cell");
      newRow.appendChild(td);
    });
    
    tbody.appendChild(newRow);
    
    // Yeni satırı veritabanına kaydet
    updateTableData([{
      action: "add_row",
      row_index: newRowIndex,
      columns: Array.from(columns).map(col => ({
        column_name: col.getAttribute("data-column"),
        value: ""
      }))
    }]);
  });

  // Satır silme fonksiyonu
  document.getElementById("deleteRowBtn").addEventListener("click", function() {
    const selectedRow = table.querySelector("tr.selected");
    if (selectedRow) {
      const rowIndex = selectedRow.getAttribute("data-row");
      selectedRow.remove();
      
      // Silinen satırı veritabanından kaldır
      updateTableData([{
        action: "delete_row",
        row_index: rowIndex
      }]);
    } else {
      alert("Lütfen silmek için bir satır seçin");
    }
  });

  // Satır seçme işlemi
  table.querySelector("tbody").addEventListener("click", function(e) {
    if (e.target.tagName === "TD") {
      const allRows = table.querySelectorAll("tbody tr");
      allRows.forEach(row => row.classList.remove("selected"));
      e.target.parentElement.classList.add("selected");
    }
  });

  // Hücre düzenleme işlemi
  table.addEventListener("blur", function (event) {
    if (event.target.isContentEditable) {
      const updatedValue = event.target.innerText;
      const columnName = event.target.getAttribute("data-column");
      const rowIndex = event.target.getAttribute("data-row");

      updateTableData([{
        action: "update_cell",
        row_index: rowIndex,
        column_name: columnName,
        new_value: updatedValue
      }]);
    }
  }, true);

  // Veritabanı güncelleme fonksiyonu
  function updateTableData(updatedData) {
    fetch(`/main_page/${fileName}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        file_name: fileName,
        updated_data: updatedData
      }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        console.log("Başarıyla güncellendi");
      } else {
        console.error("Güncelleme hatası:", data.message);
      }
    })
    .catch(error => console.error("AJAX hatası:", error));
  }
});
