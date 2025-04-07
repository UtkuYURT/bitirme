function sendRequest() {
  const prompt = document.getElementById("prompt").value;
  const imageInput = document.getElementById("image-upload");
  const formData = new FormData();

  if (prompt.trim() === "" && !imageInput.files.length) {
    alert("Lütfen bir prompt girin veya bir resim yükleyin.");
    return;
  }

  // Görselleri göndere tıklayınca göster
  const uploadedImagesContainer = document.getElementById("uploaded-images");
  uploadedImagesContainer.innerHTML = ""; // Önceki görselleri temizle
  if (imageInput.files.length) {
    for (let i = 0; i < imageInput.files.length; i++) {
      const file = imageInput.files[i];
      const reader = new FileReader();

      reader.onload = function (e) {
        const img = document.createElement("img");
        img.src = e.target.result; // base64 görsel
        img.style.maxWidth = "150px";
        img.style.maxHeight = "150px";
        img.style.border = "1px solid #ccc";
        uploadedImagesContainer.appendChild(img);
      };

      reader.readAsDataURL(file); // Görseli base64'e dönüştür
    }
  }

  formData.append("input", prompt);
  if (imageInput.files.length) {
    for (let i = 0; i < imageInput.files.length; i++) {
      formData.append("image", imageInput.files[i]);
    }
  }

  document.getElementById("spinner").style.display = "block";
  document.getElementById("response").innerHTML = "";

  fetch("/ollama", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("spinner").style.display = "none";

      if (data.success) {
        const chatHistory = document.getElementById("chat-history");

        // Kullanıcı mesajı
        const userMessage = document.createElement("div");
        userMessage.className = "user-message";
        userMessage.innerText = `Kullanıcı: ${prompt}`;
        chatHistory.appendChild(userMessage);

        // Model yanıtını
        const modelMessage = document.createElement("div");
        modelMessage.className = "model-message";
        modelMessage.innerText = `Model: ${data.response}`;
        chatHistory.appendChild(modelMessage);

        // Birleştirilmiş görsel
        if (data.merged_image_url) {
          const mergedImage = document.getElementById("merged-image");
          mergedImage.src = data.merged_image_url;
          mergedImage.style.display = "block";
        }

        // Sohbet geçmişini kaydır
        chatHistory.scrollTop = chatHistory.scrollHeight;

        document.getElementById("response").innerHTML = "";
        document.getElementById("prompt").value = "";
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
