document.addEventListener("DOMContentLoaded", function () {
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
