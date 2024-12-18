document.addEventListener("DOMContentLoaded", function () {
  const fileName = document
    .getElementById("file_div")
    .getAttribute("data-file-name");
  const table = document.getElementById("editable-table"); // Tablo ID'si

  table.addEventListener(
    "blur",
    function (event) {
      if (event.target.isContentEditable) {
        const updatedValue = event.target.innerText; // Yeni hücre değeri
        const columnName = event.target.getAttribute("data-column"); // Kolon adı
        const rowIndex = event.target.getAttribute("data-row"); // Satır indexi

        const updatedData = [
          {
            row_index: rowIndex,
            column_name: columnName,
            new_value: updatedValue,
          },
        ];

        // AJAX isteği gönder
        fetch(`/main_page/${fileName}`, {
          // file_name'i Flask'tan alıyoruz
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            file_name: fileName, // Flask'tan gelen dosya adı
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
