document.addEventListener("DOMContentLoaded", function () {
    const alertContainer = document.querySelector(".alert-container");
    const formContainer = document.querySelector(".form-container-home");

    if (alertContainer) {
      // Eğer alert mesajı varsa, formun üstüne margin-top ekle
      formContainer.style.marginTop = "50px";
    }
  });
  document.addEventListener("DOMContentLoaded", function () {
    const alertContainer = document.querySelector(".alert-container");
    const formContainer = document.querySelector(".form-container-home");
  
    if (alertContainer) {
      // Alert göründüğünde forma margin ekleyelim
      formContainer.style.marginTop = `${alertContainer.offsetHeight}px`;
  
      setTimeout(() => {
        // Alert kaybolma animasyonu
        alertContainer.style.opacity = "0";
        setTimeout(() => {
          alertContainer.remove(); // DOM'dan kaldırılıyor
          formContainer.style.marginTop = "0"; // Eski haline dön
        }, 500); // Geçiş süresi
      }, 2500); // 5 saniye bekleme
    }
  });