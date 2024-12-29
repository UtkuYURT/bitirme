document.addEventListener("DOMContentLoaded", function () {
  if (typeof $ !== "undefined") {
    $(document).ready(function () {
      if ($(".sidebar-control").length) {
        console.log("Sidebar bulundu");
      }
    });
  }

  const fileName = document
    .getElementById("file_div")
    .getAttribute("data-file-name");
  const table = document.getElementById("editable-table");

  table.addEventListener(
    "blur",
    function (event) {
      if (event.target.isContentEditable) {
        const updatedValue = event.target.innerText;
        const columnName = event.target.getAttribute("data-column");
        const rowIndex = event.target.getAttribute("data-row");

        // ! Kontrol
        // console.log(
        //   `Row Index: ${rowIndex}, Column Name: ${columnName}, New Value: ${updatedValue}`
        // );

        let updatedData = [];

        if (rowIndex === null) {
          // Sütun adı güncelleme
          updatedData = [
            {
              column_name: columnName,
              new_value: updatedValue,
            },
          ];
        } else {
          // Satır hücresinin güncellenmesi durumu
          updatedData = [
            {
              row_index: rowIndex,
              column_name: columnName,
              new_value: updatedValue,
            },
          ];
        }

        fetch(`/main_page/${fileName}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            file_name: fileName,
            updated_data: updatedData,
          }),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              console.log("Başarıyla güncellendi");
            } else {
              console.error("Güncelleme hatası:", data.message);
            }
          })
          .catch((error) => console.error("AJAX hatası:", error));
      }
    },
    true
  );
});

document.addEventListener("DOMContentLoaded", function () {
  const addRowButton = document.getElementById("add-row-button");
  const table = document.getElementById("editable-table");
  const fileDiv = document.getElementById("file_div");

  if (addRowButton && table && fileDiv) {
    addRowButton.addEventListener("click", function () {
      try {
        const tbody = table.querySelector("tbody");
        if (!tbody) {
          console.error("Tablo gövdesi bulunamadı");
          return;
        }

        const rows = tbody.getElementsByTagName("tr");
        const newRowIndex = rows.length; // Yeni satır indeksi

        // Yeni satır oluştur
        const newRow = document.createElement("tr");
        newRow.setAttribute("data-row", newRowIndex);

        // Sütun başlıklarını al
        const headers = table.querySelectorAll("th");
        const columnData = [];

        // Her sütun için boş hücre oluştur
        headers.forEach((header) => {
          const columnName = header.getAttribute("data-column");
          columnData.push({
            column_name: columnName,
            value: "", // Yeni satır için boş değer
          });

          const cell = document.createElement("td");
          cell.setAttribute("contenteditable", "true");
          cell.setAttribute("data-column", columnName);
          cell.setAttribute("data-row", newRowIndex);
          cell.classList.add("editable-cell");
          cell.textContent = "";
          newRow.appendChild(cell);
        });

        tbody.appendChild(newRow);

        // Veritabanını güncelle
        const fileName = fileDiv.getAttribute("data-file-name");
        const updatedData = [
          {
            is_new_row: true,
            row_index: newRowIndex, // Satır indeksini ekle
            columns: columnData,
          },
        ];

        console.log("Gönderilen veri:", updatedData);

        // Veritabanı güncelleme isteği
        fetch(`/main_page/${fileName}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({
            updated_data: updatedData,
          }),
        })
          .then((response) => {
            console.log("Server yanıtı:", response);
            return response.json();
          })
          .then((data) => {
            console.log("İşlem sonucu:", data);
            if (data.success) {
              console.log("Yeni satır başarıyla eklendi ve kaydedildi");
              // Başarılı güncelleme sonrası sayfayı yenileme
              // window.location.reload(); // İsteğe bağlı
            } else {
              console.error("Satır eklenirken hata oluştu:", data.message);
            }
          })
          .catch((error) => {
            console.error("AJAX hatası:", error);
          });
      } catch (error) {
        console.error("İşlem sırasında hata oluştu:", error);
      }
    });
  } else {
    console.warn("Gerekli elementlerden biri veya birkaçı bulunamadı");
  }
});

function updateDatabase(fileName, updatedData) {
  fetch(`/main_page/${fileName}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ updated_data: updatedData }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        console.log("Satır başarıyla eklendi");
      } else {
        console.error("Satır eklenirken hata oluştu:", data.message);
      }
    })
    .catch((error) => {
      console.error("Hata:", error);
    });
}

document.addEventListener("DOMContentLoaded", function () {
  const table = document.getElementById("editable-table");
  let selectedRow = null;

  // Satır seçme işlemi
  if (table) {
    table.addEventListener("click", function (e) {
      const row = e.target.closest("tr");
      if (row) {
        // Önceki seçili satırın vurgulamasını kaldır
        if (selectedRow) {
          selectedRow.classList.remove("selected-row");
        }
        // Yeni satırı seç ve vurgula
        selectedRow = row;
        row.classList.add("selected-row");
      }
    });
  }

  // Satır silme butonu
  const deleteRowButton = document.getElementById("delete-row-button");
  if (deleteRowButton) {
    deleteRowButton.addEventListener("click", function () {
      if (!selectedRow) {
        alert("Lütfen silmek için bir satır seçin");
        return;
      }

      const rowIndex = selectedRow.getAttribute("data-row");
      const fileName = document
        .getElementById("file_div")
        .getAttribute("data-file-name");

      // Silme işlemi için backend'e istek gönder
      fetch(`/main_page/${fileName}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          updated_data: [
            {
              delete_row: true,
              row_index: parseInt(rowIndex),
            },
          ],
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Başarılı silme işlemi sonrası satırı DOM'dan kaldır
            selectedRow.remove();
            selectedRow = null;
            console.log("Satır başarıyla silindi");
          } else {
            console.error("Satır silinirken hata oluştu:", data.message);
          }
        })
        .catch((error) => {
          console.error("Silme işlemi sırasında hata:", error);
        });
    });
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const addColumnButton = document.getElementById("add-column-button");
  console.log("Sütun ekleme butonu:", addColumnButton);

  if (addColumnButton) {
    console.log("Buton bulundu, event listener ekleniyor");
    addColumnButton.addEventListener("click", function () {
      console.log("Butona tıklandı");

      // Yeni sütun adını kullanıcıdan al
      const newColumnName = prompt("Yeni sütun adını giriniz:");

      // Eğer kullanıcı iptal ederse veya boş isim girerse işlemi iptal et
      if (!newColumnName || newColumnName.trim() === "") {
        return;
      }

      const table = document.getElementById("editable-table");
      const fileName = document
        .getElementById("file_div")
        .getAttribute("data-file-name");

      // Header'a yeni sütun ekle
      const headerRow = table.querySelector("thead tr");
      const newHeader = document.createElement("th");
      newHeader.setAttribute("contenteditable", "true");
      newHeader.setAttribute("data-column", newColumnName);
      newHeader.textContent = newColumnName;
      headerRow.appendChild(newHeader);

      // Tüm mevcut satırlara yeni boş hücre ekle
      const rows = table.querySelectorAll("tbody tr");
      rows.forEach((row, rowIndex) => {
        const newCell = document.createElement("td");
        newCell.setAttribute("contenteditable", "true");
        newCell.setAttribute("data-column", newColumnName);
        newCell.setAttribute("data-row", rowIndex);
        newCell.classList.add("editable-cell");
        row.appendChild(newCell);
      });

      // Veritabanını güncelle
      fetch(`/main_page/${fileName}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          updated_data: [
            {
              add_column: true,
              column_name: newColumnName,
            },
          ],
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            console.log("Yeni sütun başarıyla eklendi");
          } else {
            console.error("Sütun eklenirken hata oluştu:", data.message);
          }
        })
        .catch((error) => {
          console.error("AJAX hatası:", error);
        });
    });
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const table = document.getElementById("editable-table");
  let selectedColumn = null;

  // Sütun seçme işlemi
  if (table) {
    table.addEventListener("click", function (e) {
      const cell = e.target.closest("th, td");
      if (cell) {
        const columnName = cell.getAttribute("data-column");
        if (columnName) {
          // Önceki seçili sütunun vurgulamasını kaldır
          if (selectedColumn) {
            table
              .querySelectorAll(`[data-column="${selectedColumn}"]`)
              .forEach((cell) => {
                cell.classList.remove("selected-column");
              });
          }

          // Yeni sütunu seç ve vurgula
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

  // Sütun silme butonu
  const deleteColumnButton = document.getElementById("delete-column-button");
  if (deleteColumnButton) {
    deleteColumnButton.addEventListener("click", function () {
      if (!selectedColumn) {
        alert("Lütfen silmek için bir sütun seçin");
        return;
      }

      const fileName = document
        .getElementById("file_div")
        .getAttribute("data-file-name");

      // Silme işlemi için backend'e istek gönder
      fetch(`/main_page/${fileName}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          updated_data: [
            {
              delete_column: true,
              column_name: selectedColumn,
            },
          ],
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Başarılı silme işlemi sonrası sütunu DOM'dan kaldır
            table
              .querySelectorAll(`[data-column="${selectedColumn}"]`)
              .forEach((cell) => {
                cell.remove();
              });
            selectedColumn = null;
            console.log("Sütun başarıyla silindi");
          } else {
            console.error("Sütun silinirken hata oluştu:", data.message);
          }
        })
        .catch((error) => {
          console.error("Silme işlemi sırasında hata:", error);
        });
    });
  }
});
