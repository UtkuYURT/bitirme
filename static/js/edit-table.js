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
