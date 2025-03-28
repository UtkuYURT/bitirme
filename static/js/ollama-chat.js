function sendRequest() {
  const prompt = document.getElementById("prompt").value;
  const imageInput = document.getElementById("image-upload");
  const formData = new FormData();

  if (prompt.trim() === "" && !imageInput.files.length) {
    alert("Lütfen bir prompt girin veya bir resim yükleyin.");
    return;
  }

  formData.append("input", prompt);
  if (imageInput.files.length) {
    formData.append("image", imageInput.files[0]);
  }

  // Spinner'ı göster
  document.getElementById("spinner").style.display = "block";
  document.getElementById("response").innerHTML = "";

  fetch("/ollama", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      // Spinner'ı gizle
      document.getElementById("spinner").style.display = "none";

      if (data.success) {
        document.getElementById(
          "response"
        ).innerHTML = `<strong>Ollama Yanıtı:</strong><br>${data.response}`;
      } else {
        document.getElementById(
          "response"
        ).innerHTML = `<strong>Hata:</strong> ${data.error}`;
      }
    })
    .catch((error) => {
      console.error("Hata:", error);
      document.getElementById("spinner").style.display = "none";
      document.getElementById("response").innerHTML =
        "Bir hata oluştu. Lütfen tekrar deneyin.";
    });
}

function sendToOllama() {
  const userInput = document.getElementById("prompt").value;

  fetch("{{ url_for('ollama_interact') }}", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ input: userInput }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        document.getElementById("response").innerText =
          "Ollama'dan Gelen Yanıt: " + data.response;
      } else {
        alert("Bir hata oluştu: " + data.error);
      }
    })
    .catch((error) => {
      console.error("Hata:", error);
      alert("Bir hata oluştu.");
    });
}
