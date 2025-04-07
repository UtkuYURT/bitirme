document.addEventListener("DOMContentLoaded", () => {
  const rows = document.querySelectorAll(".table-operation-logs tbody tr");

  rows.forEach((row) => {
    row.addEventListener("click", (event) => {
      const clickedCell = event.target;
      const lastCell = row.querySelector("td:last-child");

      // tıklanan hücre son sütunsa seçme
      if (clickedCell === lastCell || clickedCell.closest("button")) {
        return;
      }

      row.classList.toggle("selected");
    });
  });
});

function sendSelectedRowsToOllama() {
  const selectedRows = [];
  const rows = document.querySelectorAll(
    ".table-operation-logs tbody tr.selected"
  );

  // Seçili satır yoksa veya bir satır seçiliyse işlemi yapma
  if (rows.length <= 1) {
    alert("Lütfen en az iki satır seçin!");
    return;
  }

  rows.forEach((row) => {
    const operationType = row.querySelector("td:nth-child(1)").innerText.trim();
    const inputValues = row.querySelector("td:nth-child(2)").innerText.trim();
    const result = row.querySelector("td:nth-child(3)").innerText.trim();
    const graph = row.querySelector("td:nth-child(4) img").src.trim();
    selectedRows.push({ operationType, inputValues, result, graph });
  });

  fetch("/ollama_operation_chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ selectedRows }),
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
  console.log("[DEBUG] Silme işlemi için gönderilen değerler:");
  console.log("[DEBUG] Operation:", operation);
  console.log("[DEBUG] Input Values:", inputValues);
  console.log("[DEBUG] Result:", result);
  console.log("[DEBUG] Graph:", graph);

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
