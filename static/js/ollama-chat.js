function sendRequest() {
    const prompt = document.getElementById('prompt').value;
    if (prompt.trim() === "") {
        alert("Lütfen bir prompt girin.");
        return;
    }

    const data = { input: prompt };

    // Spinner'ı göster
    document.getElementById('spinner').style.display = 'block';
    document.getElementById('response').innerHTML = '';

    fetch('http://localhost:5000/ollama', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        // Spinner'ı gizle
        document.getElementById('spinner').style.display = 'none';

        if (data.success) {
            document.getElementById('response').innerHTML = `<strong>Ollama Yanıtı:</strong><br>${data.response}`;
        } else {
            document.getElementById('response').innerHTML = `<strong>Hata:</strong> ${data.error}`;
        }
    })
    .catch(error => {
        console.error('Hata:', error);
        document.getElementById('spinner').style.display = 'none';
        document.getElementById('response').innerHTML = 'Bir hata oluştu. Lütfen tekrar deneyin.';
    });
}