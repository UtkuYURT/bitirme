import requests

# Flask API'nin çalıştığı URL
url = "http://localhost:5000/ollama"

# API'ye gönderilecek veri
data = {"input": "Merhaba! Nasılsın?"}

# Flask API'ye POST isteği gönder
response = requests.post(url, json=data)

# Yanıtı kontrol et ve ekrana yazdır
if response.status_code == 200:
    try:
        json_response = response.json()
        if json_response.get("success"):
            print("Ollama Yanıtı:")
            print(json_response.get("response"))
        else:
            print("Hata:", json_response.get("error"))
    except ValueError:
        print("Yanıt JSON formatında değil:", response.text)
else:
    print(f"HTTP Hatası: {response.status_code}")