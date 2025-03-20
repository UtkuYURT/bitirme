from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from db import *
from flask_cors import CORS 
import pandas as pd
import numpy as np
import requests
import os
import json


app = Flask(__name__)
CORS(app)

app.secret_key = 'gizli_anahtar'

# ? DB Settings 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'bitirme'

init_db(app)

create_database()
with app.app_context():
    create_tables()

# ! Yardımcı Fonksiyonlar
def is_user_logged_in():
    return session.get('user_id')

def get_file_extension(file_name):
    return os.path.splitext(file_name)[1].lower().strip('.')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_file_upload(user_id, file):
    if file and allowed_file(file.filename):
        filename = file.filename
        file_content = file.read()
        save_files(user_id, filename, file_content)
        flash("Dosya başarıyla kaydedildi", "file_success")
    else:
        flash("Geçersiz dosya türü.", "file_danger")

def generate_table_html(df, editable=False):
    table_id = "editable-table" if editable else "analysis-table"
    table_html = f'<table class="table table-bordered table-hover table-striped" id="{table_id}">'
    table_html += '<thead><tr>'
    for col in df.columns:
        # Sütun başlıklarına data-column özelliği ekleniyor
        contenteditable_attr = 'contenteditable="true"' if editable else ''
        table_html += f'<th class="editable-header" data-column="{col}" {contenteditable_attr}>{col}</th>'
    table_html += '</tr></thead><tbody>'
    for i, row in df.iterrows():
        table_html += f'<tr data-row="{i}">'
        for col in df.columns:
            cell_class = "editable-cell" if editable else "analysis-cell"
            contenteditable_attr = 'contenteditable="true"' if editable else ''
            table_html += f'<td class="{cell_class}" data-column="{col}" data-row="{i}" {contenteditable_attr}>{row[col]}</td>'
        table_html += '</tr>'
    table_html += '</tbody></table>'
    return table_html

# ! Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def sign_in_route():
    if request.method == 'POST':
        email = request.form['e-mail']
        password = request.form['sifre']
        user = sign_in(email, password)
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('file_operations')) 
        flash("Giriş Başarısız", "login_danger")
        return redirect(url_for('home')) 

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def sign_up_route():
    if request.method == 'POST':
        email = request.form['e-mail']
        password1 = request.form['sifre']
        password2 = request.form['sifre2']
        if password1 == password2:
            sign_up(email, password1)
            flash("Kayıt Başarılı", "login_success")
            return redirect(url_for('home')) 
        flash("Kayıt Başarısız", "login_danger")
        return redirect(url_for('register'))

@app.route('/file_operations')
def file_operations():
    user_id = is_user_logged_in()
    if user_id:
        files = get_files(user_id) 
        return render_template("file_operations.html", files=files)
    flash("Kullanıcı bulunamadı", "file_danger")
    return redirect(url_for("home"))

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        user_id = is_user_logged_in()
        if user_id:
            file = request.files.get('file')
            if file:
                handle_file_upload(user_id, file)
            else:
                flash("Dosya alınamadı. Lütfen tekrar deneyin.", "file_danger")
        else:
            flash("Kullanıcı bulunamadı", "file_danger")
        return redirect(url_for("file_operations"))

@app.route('/delete_file', methods=['POST'])
def delete_file():
    if request.method == 'POST':
        user_id = is_user_logged_in()
        if user_id:
            file_name = request.form.get('file_name') 
            if file_name:
                try:
                    delete_files(user_id, file_name)
                    flash(f"'{file_name}' dosyası başarıyla silindi.", "file_success")
                except Exception as e:
                    flash(f"Bir hata oluştu: {str(e)}", "danger")
            else:
                flash("Silmek için geçerli bir dosya adı alınamadı.", "file_danger")
        else:
            flash("Kullanıcı bulunamadı. Lütfen tekrar giriş yapın.", "file_danger")
    return redirect(url_for('file_operations'))

@app.route('/main_page')
def main_page():
    return render_template('main_page.html')

@app.route('/main_page/<file_name>', methods=['GET', 'POST'])
def view_file(file_name):
    user_id = is_user_logged_in()

    if not user_id:
        flash("Kullanıcı giriş yapmamış", "file_danger")
        return redirect(url_for('login'))

    if request.method == 'GET':
        file_extension = get_file_extension(file_name)
        try:
            file_content = get_file_data(user_id, file_name, file_type=file_extension)

            if file_content is None or not isinstance(file_content, pd.DataFrame):
                flash("Dosya bulunamadı veya içerik mevcut değil", "file_danger")
                return redirect(url_for('file_operations'))

            if file_content.empty:
                flash("Dosya boş", "file_danger")
                return redirect(url_for('file_operations'))

            table_html = generate_table_html(file_content, editable=True)
            return render_template('main_page.html', file_name=file_name, content=table_html)

        except Exception as e:
            print(f"Hata oluştu: {e}")
            flash("Bir hata oluştu. Lütfen tekrar deneyin.", "file_danger")
            return redirect(url_for('file_operations'))
    else: 
        try:
            data = request.get_json()
            updated_data = data.get('updated_data', [])
            result = update_table_data(user_id, file_name, updated_data)
            if isinstance(result, str) and "hata" in result.lower():
                return jsonify({"success": False, "message": result})
            return jsonify({"success": True, "message": "Veriler başarıyla güncellendi"})
        except Exception as e:
            print(f"Hata oluştu: {str(e)}")
            return jsonify({"success": False, "message": f"Hata: {str(e)}"})
        
@app.route('/analysis_processes')
def analysis_page():
    return render_template('analysis.html')

@app.route('/analysis_processes/<file_name>', methods=['GET', 'POST'])
def analysis(file_name):
    user_id = is_user_logged_in()

    if not user_id:
        flash("Kullanıcı giriş yapmamış", "file_danger")
        return redirect(url_for('login'))

    if request.method == 'GET':
        file_extension = get_file_extension(file_name)
        file_content = get_file_data(user_id, file_name, file_type=file_extension)
        if file_content is not None and isinstance(file_content, pd.DataFrame):
            if not file_content.empty:
                table_html = generate_table_html(file_content, editable=False)
                return render_template('analysis.html', file_name=file_name, content=table_html)
            flash("Dosya boş", "file_danger")
        else:
            flash("Dosya bulunamadı veya içerik mevcut değil", "file_danger")
        return redirect(url_for('file_operations'))
        
OPERATIONS = {
    'arithmetic': {
        'function': lambda values: np.mean(values),
        'title': 'Aritmetik Ortalama'
    },
    'geometric': {
        'function': lambda values: np.prod(values) ** (1 / len(values)),
        'title': 'Geometrik Ortalama'
    },
    'harmonic': {
        'function': lambda values: len(values) / np.sum(1 / np.array(values)),
        'title': 'Harmonik Ortalama'
    },
}
    
@app.route('/mathematical_operations', methods=['GET', 'POST'])
def mathematical_operations():
    if request.method == 'POST':
        data = request.get_json()
        selected_values = request.get_json().get('selectedValues', [])
        operation = data.get('operation', 'arithmetic')

        try:
            numeric_values = np.array([float(value) for value in selected_values if value.replace('.', '', 1).isdigit()])
            if numeric_values.size > 0:
                operation_data = OPERATIONS.get(operation, {})
                result = operation_data.get('function', lambda values: None)(numeric_values)
                title = operation_data.get('title', 'Matematiksel İşlem')
            else:
                result = None
                title = 'Matematiksel İşlem'
        except Exception as e:
            return jsonify({"error": str(e)}), 400

        # Sonucu ve seçilmiş sayıları session'a kaydet
        session['result'] = result
        session['selected_values'] = selected_values
        session['operation'] = operation
        session['operation_title'] = title

        # Yönlendirme URL'sini döndür
        return jsonify({"redirect_url": url_for('mathematical_operations')})

    else:
        result = session.get('result', None)
        selected_values = session.get('selected_values', [])
        operation = session.get('operation', 'arithmetic')
        title = session.get('operation_title', 'Matematiksel İşlem')
        return render_template('mathematical_operations.html', result=result, selected_values=selected_values, operation=operation, title=title)
  # Ollama chat sayfası

@app.route('/rollback', methods=['POST', 'GET'])
def rollback():
    user_id = is_user_logged_in()
    if request.method == 'GET':
        file_name = request.args.get('file_name') 
        if not user_id or not file_name:
            flash("Eksik parametreler", "file_danger")
            return redirect(url_for('main_page'))

        logs = get_logs(file_name, user_id)  
        if not logs:
            flash("Log verileri alınamadı", "file_danger")
            return redirect(url_for('main_page'))
        
        return render_template('rollback.html', logs=logs, file_name=file_name)
    else:
        file_name = request.form.get('file_name')
        log_id = request.form.get('log_id')

        if not user_id or not file_name or not log_id:
            flash("Eksik parametreler", "file_danger")
            return redirect(url_for('rollback', file_name=file_name))

        result = rollback_change(user_id, file_name, log_id)
        flash(result, "file_success" if "başarıyla" in result else "file_danger")
        return redirect(url_for('rollback', file_name=file_name))
    
# !! OLLAMA 
@app.route('/ollama_chat')
def ollama_chat():
    return render_template('ollama_chat.html')  # ollama_chat.html dosyasını render et
      
# Ollama API 'YE İstek Gönderme
@app.route('/ollama', methods=['POST'])
def ollama_interact():
    # Kullanıcıdan gelen metni al
    user_input = request.json.get('input', '')

    # Ollama API'sine istek gönder
    response = requests.post(
        'http://127.0.0.1:11434/api/generate',  # Ollama sunucu adresi
        json={
            "model": "mistral",  # Buraya kullanmak istediğin modeli yaz
            "prompt": user_input
        },
        stream=True  # Streaming yanıtları işlemek için
    )

    # Yanıtı parça parça işlemek için birikmiş metni tutacak bir değişken
    full_response = ""

    # Streaming yanıtları işleme
    if response.status_code == 200:
        try:
            for line in response.iter_lines():
                if line:  # Boş olmayan satırları işle
                    try:
                        # Her bir JSON nesnesini ayrıştır
                        json_line = json.loads(line.decode('utf-8'))
                        # Yanıt metnini biriktir
                        full_response += json_line.get("response", "")
                    except json.JSONDecodeError as e:
                        print(f"JSON ayrıştırma hatası: {str(e)}")
            
            # Tam yanıtı döndür
            return jsonify({"success": True, "response": full_response})
        except Exception as e:
            return jsonify({"error": f"Streaming işleme hatası: {str(e)}"}), 500
    else:
        return jsonify({"error": "Ollama yanıt vermedi", "status_code": response.status_code}), 500
# !! OLLLAMA 

if __name__ == '__main__':
    app.run(debug=True)
