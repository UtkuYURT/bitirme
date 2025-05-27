document.addEventListener("DOMContentLoaded", () => {
  const rows = document.querySelectorAll(".table-operation-logs tbody tr");

  rows.forEach((row) => {
    row.addEventListener("click", (event) => {
      const clickedCell = event.target;
      const lastCell = row.querySelector("td:last-child");
      const fourthCell = row.querySelector("td:nth-child(4)");

      // Eğer tıklanan hücre son sütun veya 4. sütun ise veya bir buton varsa, seçim engellenir
      if (
        clickedCell === lastCell ||
        clickedCell === fourthCell ||
        clickedCell.closest("button")
      ) {
        return;
      }

      // Eğer görsele tıklanırsa modal açılacak, satır seçimi engellenecek
      if (clickedCell.tagName === "IMG") {
        event.preventDefault(); // Satır seçimini engelle
        openModal(clickedCell); // Modal açma fonksiyonu
        return;
      }

      // Satır seçme işlemi
      row.classList.toggle("selected");
    });
  });

  // Modal açma fonksiyonu (örnek)
  function openModal(image) {
    const modal = document.getElementById("myModal");
    const modalImage = modal.querySelector("img");
    const modalCaption = modal.querySelector(".modal-caption");

    const inputValues = image
      .closest("tr")
      .querySelector("td:nth-child(2)")
      .innerText.trim();
    const result = image
      .closest("tr")
      .querySelector("td:nth-child(3)")
      .innerText.trim();

    // Modalda görseli güncelle
    modalImage.src = image.src;
    modalCaption.innerHTML = `
                              <strong>Girdi Değerleri:</strong> ${inputValues} <br>
                              <strong>Sonuç:</strong> ${result}`; // Görselin açıklaması ve işlem bilgileri

    // Modali göster
    modal.style.display = "block";

    // Modal kapama
    const closeBtn = modal.querySelector(".close");
    closeBtn.onclick = function () {
      modal.style.display = "none";
    };

    // Modal dışında bir yere tıklayınca kapama
    window.onclick = function (event) {
      if (event.target === modal) {
        modal.style.display = "none";
      }
    };
  }
});

function sendSelectedRowsToOllama() {
  const selectedRows = [];
  const rows = document.querySelectorAll(
    ".table-operation-logs tbody tr.selected"
  );

  // Aktif log türünü belirle (görünür olan satırların operationType'ına bakarak)
  const visibleRow = Array.from(
    document.querySelectorAll(".table-operation-logs tbody tr")
  ).find((row) => row.style.display !== "none");

  const operationType = visibleRow?.dataset?.operation || "";
  const isTextual = [
    "keyword_extraction",
    "summarization",
    "main_information",
    "frequency",
    "emotion",
  ].includes(operationType);

  // Seçili satır sayısı kontrolü
  if ((isTextual && rows.length < 1) || (!isTextual && rows.length < 2)) {
    alert(
      isTextual
        ? "Lütfen en az bir satır seçin"
        : "Lütfen en az iki satır seçin"
    );
    return;
  }

  rows.forEach((row) => {
    const operationType = row.querySelector("td:nth-child(1)").innerText.trim();
    const inputValues = row.querySelector("td:nth-child(2)").innerText.trim();
    const result = row.querySelector("td:nth-child(3)").innerText.trim();
    const rowData = {
      operationType,
      inputValues,
      result,
    };

    if (!isTextual) {
      const graphImg = row.querySelector("td:nth-child(4) img");
      rowData.graph = graphImg ? graphImg.src.trim() : null;
    }

    selectedRows.push(rowData);
    console.log("Seçilen Satır:", selectedRows);
  });

  fetch("/ollama_operation_chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      selectedRows,
      operationType: operationType || "",
    }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP Hatası! Durum: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        window.location.href = "/ollama_operation_chat";
      } else {
        alert("Bir hata oluştu: " + data.error);
      }
    })
    .catch((error) => {
      console.error("Hata:", error.message || error);
      alert("Bir hata oluştu: " + (error.message || "Bilinmeyen bir hata"));
    });
}

document.addEventListener("DOMContentLoaded", () => {
  const deleteButtons = document.querySelectorAll(".delete-log-btn");

  deleteButtons.forEach((button) => {
    button.addEventListener("click", (event) => {
      const logRow = event.target.closest("tr");
      const operation = logRow.getAttribute("data-operation");
      const inputValues = logRow.getAttribute("data-input-values");
      const result = logRow.getAttribute("data-result");
      const graph = logRow.getAttribute("data-graph");

      console.log("Operation:", operation);
      console.log("Input Values:", inputValues);
      console.log("Result:", result);
      console.log("Graph:", graph);

      deleteLog(operation, inputValues, result, graph);
    });
  });
});

function deleteLog(operation, inputValues, result, graph) {
  // console.log("[DEBUG] Silme işlemi için gönderilen değerler:");
  // console.log("[DEBUG] Operation:", operation);
  // console.log("[DEBUG] Input Values:", inputValues);
  // console.log("[DEBUG] Result:", result);
  // console.log("[DEBUG] Graph:", graph);

  if (!confirm("Bu log kaydını silmek istediğinizden emin misiniz?")) {
    return;
  }

  fetch("/delete_operation_log", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      operation,
      input_values: inputValues,
      result,
      graph,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert(data.message);

        window.location.reload();
      } else {
        alert("Hata: " + data.error);
      }
    })
    .catch((error) => {
      console.error("Hata:", error);
      alert("Bir hata oluştu.");
    });
}

function selectLogsType() {
  const mathematicalLogsButton = document.getElementById(
    "mathematical-logs-btn"
  );
  const textualLogsButton = document.getElementById("textual-logs-btn");
  const logRows = document.querySelectorAll(".table-operation-logs tbody tr");
  const logsTableContainer = document.getElementById("logs-table");

  const textualOperations = [
    "keyword_extraction",
    "summarization",
    "main_information",
    "frequency",
    "emotion",
  ];

  function clearSelectedRows() {
    document
      .querySelectorAll(".table-operation-logs tbody tr.selected")
      .forEach((row) => row.classList.remove("selected"));
  }

  // Metinsel logları göster
  textualLogsButton.addEventListener("click", (e) => {
    e.preventDefault();
    logsTableContainer.style.display = "block";
    clearSelectedRows();
    logRows.forEach((row) => {
      const operationType = row.dataset.operation;
      row.style.display = textualOperations.includes(operationType)
        ? ""
        : "none";
    });
  });

  // Matematiksel logları göster
  mathematicalLogsButton.addEventListener("click", (e) => {
    e.preventDefault();
    logsTableContainer.style.display = "block";
    clearSelectedRows();
    logRows.forEach((row) => {
      const operationType = row.dataset.operation;
      row.style.display = !textualOperations.includes(operationType)
        ? ""
        : "none";
    });
  });
}

selectLogsType();

// ! Pdf indirme
document.addEventListener("DOMContentLoaded", function () {
  const downloadButtons = document.querySelectorAll(".download-pdf-btn");

  downloadButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const operation = encodeURIComponent(
        button.getAttribute("data-operation")
      );
      const inputValues = encodeURIComponent(
        button.getAttribute("data-input-values")
      );
      const result = encodeURIComponent(button.getAttribute("data-result"));
      const graph = encodeURIComponent(button.getAttribute("data-graph"));

      const url = `/download_log_pdf?operation=${operation}&input_values=${inputValues}&result=${result}&graph=${graph}`;
      window.open(url, "_blank");
    });
  });
});
