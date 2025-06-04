function autoResize(textarea) {
  textarea.style.height = "auto"; // önce sıfırla
  textarea.style.height = Math.min(textarea.scrollHeight, 500) + "px"; // max 500px
}

function sendRequest() {
  const prompt = document.getElementById("prompt").value;
  const imageInput = document.getElementById("image-upload");
  const formData = new FormData();

  if (prompt.trim() === "" && !imageInput.files.length) {
    alert("Lütfen bir prompt girin veya bir resim yükleyin.");
    return;
  }

  const spinner = document.getElementById("spinner");
  const loadingIndicator = document.getElementById("loading-indicator"); // 🔁 Loader elementini al
  const submitButton = document.getElementById("prompt-button");

  // Eğer spinner aktifse butonu devre dışı bırak
  if (spinner.classList.contains("d-block")) {
    submitButton.disabled = true;
    return;
  }

  const chatHistory = document.getElementById("chat-history");
  chatHistory.classList.remove("d-none");
  chatHistory.classList.add("d-block");

  const uploadedImagesContainer = document.getElementById("uploaded-images");
  uploadedImagesContainer.innerHTML = "";
  if (imageInput.files.length) {
    for (let i = 0; i < imageInput.files.length; i++) {
      const file = imageInput.files[i];
      const reader = new FileReader();

      reader.onload = function (e) {
        const img = document.createElement("img");
        img.src = e.target.result;
        img.style.maxWidth = "150px";
        img.style.maxHeight = "150px";
        img.style.border = "1px solid #ccc";
        uploadedImagesContainer.appendChild(img);
      };

      reader.readAsDataURL(file);
    }

    const uploadedImagesWrapper = document.getElementById(
      "uploaded-images-container"
    );
    uploadedImagesWrapper.classList.remove("d-none");
    uploadedImagesWrapper.classList.add("d-block");
  }

  formData.append("input", prompt);
  if (imageInput.files.length) {
    for (let i = 0; i < imageInput.files.length; i++) {
      formData.append("image", imageInput.files[i]);
    }
  }

  // ✅ Spinner ve loading-indicator'ı göster
  spinner.classList.remove("d-none");
  spinner.classList.add("d-block");

  loadingIndicator.style.display = "block"; // 👈 loader görünür olsun
  submitButton.disabled = true;

  document.getElementById("response").innerHTML = "";

  fetch("/ollama", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      spinner.classList.remove("d-block");
      spinner.classList.add("d-none");

      loadingIndicator.style.display = "none"; // 👈 loader gizlensin
      submitButton.disabled = false;

      if (data.success) {
        const chatHistory = document.getElementById("chat-history");

        const userMessage = document.createElement("div");
        userMessage.className = "user-message";
        userMessage.innerText = `Kullanıcı: ${prompt}`;
        chatHistory.appendChild(userMessage);

        const modelMessage = document.createElement("div");
        modelMessage.className = "model-message";
        modelMessage.innerText = `Model: ${data.response}`;
        chatHistory.appendChild(modelMessage);

        if (data.merged_image_url) {
          const mergedImage = document.getElementById("merged-image");
          mergedImage.src = data.merged_image_url;
          mergedImage.style.display = "block";
        }

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
      spinner.classList.remove("d-block");
      spinner.classList.add("d-none");

      loadingIndicator.style.display = "none"; // 👈 loader gizlensin
      submitButton.disabled = false;
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
