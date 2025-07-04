from flask import Flask, render_template,  make_response, request, redirect, url_for, flash, session, jsonify, send_file
from db import *
from flask_cors import CORS 
import pandas as pd
import numpy as np
import requests
import os
import json
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LinearRegression
import base64
from PIL import Image
import io
from googletrans import Translator
from fpdf import FPDF
from unidecode import unidecode
import pdfplumber
from docx import Document
import string

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
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'pdf', 'txt', 'docx'}
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

def create_dynamic_plot(values, operation, result):
    plt.figure(figsize=(6, 4))

    if operation == 'frequency':
        keys = list(result.keys())
        values = list(result.values())
        plt.bar(keys, values, color='blue', alpha=0.7)
        plt.title('Frekans Grafiği')
        plt.xlabel('Değerler')
        plt.ylabel('Frekans')
    elif operation == 'regression':
        X = values[:, 0]  # Bağımsız değişken
        Y = values[:, 1]  # Bağımlı değişken

        #Dağılım grafiği
        plt.scatter(X, Y, color='blue', label='Veri Noktaları')

        #Regresyon doğrusu
        slope = result.get('slope', 0)
        intercept = result.get('intercept', 0)
        regression_line = [slope * x + intercept for x in X]
        plt.plot(X, regression_line, color='red', label=f'Regresyon Doğrusu: y = {slope}x + {intercept}')

        #!Başlıklar
        plt.title('Regresyon Analizi')
        plt.xlabel('Bağımsız Değişken (X)')
        plt.ylabel('Bağımlı Değişken (Y)')
        plt.legend()
    else:
        result = round(result, 2)
        plt.plot(values, label='Veri Seti', marker='o', color='blue')
        plt.axhline(result, color='red', linestyle='--', label=f'{OPERATIONS.get(operation, {}).get("title", "Matematiksel İşlem")}: {result}')
        plt.title(f'{OPERATIONS.get(operation, {}).get("title", "Matematiksel İşlem")} Grafiği')
        plt.xlabel('Veri Sırası')
        plt.ylabel('Değer')
        plt.legend()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return img

def save_graph(values, operation, result, user_id):
    try:
        plt.figure(figsize=(6, 4))

        if operation == 'regression':
            X = values[:, 0]
            Y = values[:, 1]

            # Dağılım grafiği
            plt.scatter(X, Y, color='blue', label='Veri Noktaları')

            # Regresyon doğrusu
            slope = result.get('slope', 0)
            intercept = result.get('intercept', 0)
            regression_line = [slope * x + intercept for x in X]
            plt.plot(X, regression_line, color='red', label=f'Regresyon Doğrusu: y = {slope}x + {intercept}')

            #!Başlıklar
            plt.title('Regresyon Analizi')
            plt.xlabel('Bağımsız Değişken (X)')
            plt.ylabel('Bağımlı Değişken (Y)')
            plt.legend()

        else:
            # Aritmetik ortalama vb. grafik
            plt.plot(values, label='Veri Seti', marker='o', color='blue')
            plt.axhline(result, color='red', linestyle='--', label=f'{OPERATIONS.get(operation, {}).get("title", "Sonuç")}: {result}')
            plt.title(f'{OPERATIONS.get(operation, {}).get("title", "Matematiksel İşlem")} Grafiği')
            plt.xlabel('Veri Sırası')
            plt.ylabel('Değer')
            plt.legend()

        # Grafiği kaydet
        graph_dir = os.path.join('static', 'graphs', str(user_id))
        os.makedirs(graph_dir, exist_ok=True)
        graph_path = os.path.join(graph_dir, f"{operation}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
        plt.savefig(graph_path)
        plt.close()

        print(f"Grafik kaydedildi: {graph_path}")
        return graph_path
    except Exception as e:
        print(f"Grafik kaydetme hatası: {str(e)}")
        return None
    
def merge_images(image1, image2):
    try:
        img1 = Image.open(image1).convert("RGB")
        img2 = Image.open(image2).convert("RGB")

        # Resimlerin boyutları
        width1, height1 = img1.size
        width2, height2 = img2.size

        # Birleştirilimiş resmin genişlik - yükseklik
        total_width = width1 + width2
        max_height = max(height1, height2)

        # Boş resim
        merged_image = Image.new("RGB", (total_width, max_height), (255, 255, 255))

        merged_image.paste(img1, (0, 0))
        merged_image.paste(img2, (width1, 0))

        # Birleştirilen resmi geçici bir dosyaya kaydet
        merged_image_path = os.path.join("static", "merged_images", "merged_image.jpg")
        os.makedirs(os.path.dirname(merged_image_path), exist_ok=True)
        merged_image.save(merged_image_path)

        return merged_image_path
    except Exception as e:
        print(f"[DEBUG] Resimleri birleştirme hatası: {str(e)}")
        return None

def save_uploaded_images(image_files):
    saved_image_paths = []
    upload_dir = os.path.join("static", "uploaded_images")
    os.makedirs(upload_dir, exist_ok=True)

    for image_file in image_files:
        try:
            image_path = os.path.join(upload_dir, image_file.filename)
            image_file.save(image_path)
            saved_image_paths.append(image_path)
        except Exception as e:
            print(f"[DEBUG] Görsel kaydetme hatası: {str(e)}")
    
    return saved_image_paths

def process_selected_rows(selected_rows):
    images = []
    prompt = []

    is_textual = selected_rows[0].get('operationType') == 'main_information'

    for row in selected_rows:
        operation_type = row.get('operationType')
        input_values = row.get('inputValues')
        result = row.get('result')

        if not is_textual:
            graph = row.get('graph')
            # Görseli base64 formatına dönüştür
            graph_base64 = encode_graph_to_base64(graph)
            if graph_base64:
                images.append(graph_base64)

            # Sayısal işlem için prompt
            prompt.append(
                f"{input_values} değerleri ile {operation_type} işlemi yaptım ve sonuç olarak {result} sonucunu aldım. "
                f"Bu işleme ait grafik görselde yer alıyor."
            )
        else:
            prompt.append(
                f"Metin girdisi: \"{input_values}\""
            )

    if is_textual:
        prompt.append(f"Lütfen bu metni içerik ve anlam açısından açıklar mısın?")
    else:
        prompt.append(f"Lütfen bu {len(selected_rows)} işlemi hem sayısal hem grafiklerdeki görsel bilgiler açısından karşılaştırır mısın?")
        for i, image in enumerate(images):
            prompt.append(f"Görsel {i + 1}: {image}")

    return images, prompt

def encode_graph_to_base64(graph_path):
    try:
        with open(graph_path, "rb") as graph_file:
            return base64.b64encode(graph_file.read()).decode('utf-8')
    except Exception as e:
        print(f"[DEBUG] Grafik dosyası okunamadı: {str(e)}")
        return None

def extract_text_from_pdf(file_content):
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"PDF metni çıkarılamadı: {str(e)}")
        return "PDF metni çıkarılamadı veya dosya bozuk."
    
def extract_text_from_docx(file_content):
    try:
        doc = Document(io.BytesIO(file_content))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"DOCX metni çıkarılamadı: {str(e)}")
        return None

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

            if file_extension in ['csv', 'xlsx']:
                # CSV ve Excel dosyaları için tablo oluştur
                if not isinstance(file_content, pd.DataFrame) or file_content.empty:
                    flash("Dosya boş veya geçersiz", "file_danger")
                    return redirect(url_for('file_operations'))

                table_html = generate_table_html(file_content, editable=True)
                return render_template('main_page.html', file_name=file_name, content=table_html, is_text=False)

            elif file_extension in ['txt', 'pdf', 'docx']:
                if file_extension == 'txt':
                    try:
                        text_content = file_content.decode('utf-8')  
                    except Exception as e:
                        print(f"TXT dosyası okunamadı: {str(e)}")
                        text_content = "TXT dosyası okunamadı."
                elif file_extension == 'pdf':
                    text_content = extract_text_from_pdf(file_content) 
                elif file_extension == 'docx':
                    text_content = extract_text_from_docx(file_content) 

                if not text_content or text_content.strip() == "":
                    flash("Dosya içeriği boş veya okunamadı.", "file_danger")
                    return redirect(url_for('file_operations'))
 
                return render_template('main_page.html', file_name=file_name, content=text_content, is_text=True)

            else:
                flash("Desteklenmeyen dosya türü", "file_danger")
                return redirect(url_for('file_operations'))

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

        if file_extension in ['csv', 'xlsx']:
            if file_content is not None and isinstance(file_content, pd.DataFrame):
                if not file_content.empty:
                    table_html = generate_table_html(file_content, editable=False)
                    return render_template('analysis.html', file_name=file_name, content=table_html)
                flash("Dosya boş", "file_danger")
            else:
                flash("Dosya bulunamadı veya içerik mevcut değil", "file_danger")

        elif file_extension in ['txt', 'pdf', 'docx']:
            if file_extension == 'txt':
                try:
                    text_content = file_content.decode('utf-8')
                except Exception as e:
                    print(f"TXT dosyası okunamadı: {str(e)}")
                    text_content = "TXT dosyası okunamadı."
            elif file_extension == 'pdf':
                text_content = extract_text_from_pdf(file_content)
            elif file_extension == 'docx':
                text_content = extract_text_from_docx(file_content)

            if text_content and text_content.strip():
                return render_template('analysis.html', file_name=file_name, content=text_content, file_extension=file_extension)
            else:
                flash("Dosya içeriği boş veya okunamadı.", "file_danger")

        else:
            flash("Desteklenmeyen dosya türü", "file_danger")

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
    'median': {
        'function': lambda values: np.median(values),
        'title': 'Medyan'   
    },
    'correlation': {
        'function': lambda values: np.corrcoef(values),
        'title': 'Korelasyon Analizi'
    },
    'std_dev': { 
        'function': lambda values: np.std(values),
        'title': 'Standart Sapma'
    },
    'variance': { 
        'function': lambda values: np.var(values),
        'title': 'Varyans'
    },
    'z_test': {
        'function': lambda values: (np.mean(values) - 0) / (np.std(values) / np.sqrt(len(values))),
        'title': 'Z Testi'
    },
    't_test': {
        'function': lambda values: (np.mean(values) - 0) / (np.std(values, ddof=1) / np.sqrt(len(values))),
        'title': 'T Testi'
    },
    'regression': {
        'function': lambda values: LinearRegression().fit(values[:, 0].reshape(-1, 1), values[:, 1]),
        'title': 'Regresyon Testi'
    },
    'frequency': {
        'function': lambda values: {value: np.sum(values == value) for value in np.unique(values)},
        'title': 'Frekans'
    },
}
    
@app.route('/mathematical_operations', methods=['GET', 'POST'])
def mathematical_operations():
    if request.method == 'POST':
        data = request.get_json()
        selected_values = data.get('selectedValues', [])
        operation = data.get('operation', 'arithmetic')

        try:
            if operation == 'regression':
                numeric_values = np.array(selected_values, dtype=float).T  

                # Bağımsız değişken (X) bağımlı değişken (Y)
                X = numeric_values[:, 0].reshape(-1, 1) 
                Y = numeric_values[:, 1]  

                model = LinearRegression().fit(X, Y)
                slope = model.coef_[0] 
                intercept = model.intercept_ 

                result = {
                    'slope': round(slope, 2),
                    'intercept': round(intercept, 2),
                }
                title = 'Regresyon Testi'

                graph_path = save_graph(numeric_values, operation, result, is_user_logged_in())
            else:
                numeric_values = np.array([float(value) for value in selected_values if value.replace('.', '', 1).isdigit()])

                if numeric_values.size > 0:
                    operation_data = OPERATIONS.get(operation, {})
                    result = operation_data.get('function', lambda values: None)(numeric_values)
                    title = operation_data.get('title', 'Matematiksel İşlem')

                    if operation == 'frequency':
                        result = {str(k): int(v) for k, v in result.items()}
                        graph_path = save_graph(numeric_values, operation, result, is_user_logged_in())
                    else:
                        result = round(result, 2)
                        graph_path = save_graph(numeric_values, operation, result, is_user_logged_in())
                else:
                    result = None
                    title = 'Matematiksel İşlem'
                    graph_path = None

            user_id = is_user_logged_in() 
            log_operation(user_id, operation, selected_values, result, graph_path)

        except Exception as e:
            return jsonify({"error": str(e)}), 400

        session['result'] = result
        session['selected_values'] = selected_values
        session['operation'] = operation
        session['operation_title'] = title

        return jsonify({"redirect_url": url_for('mathematical_operations')})

    else:
        result = session.get('result', None)
        selected_values = session.get('selected_values', [])
        operation = session.get('operation', 'arithmetic')
        title = session.get('operation_title', 'Matematiksel İşlem')
        return render_template('mathematical_operations.html', result=result, selected_values=selected_values, operation=operation, title=title)

# !metin sonuçlarını alma
def get_main_idea_with_ollama(text):
    try:
        translated_prompt, detected_language = translate_prompt_if_needed(
            f"{text} \n what is the main information in this text? Can you explain it in one sentence?"
        )

        payload = {
            "model": "llava", 
            "prompt": translated_prompt,
            "stream": True
        }

        full_response = call_ollama_api(payload)

        translated_response = translate_response_if_needed(full_response, detected_language)

        return translated_response.strip()
    
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

def get_keyword_with_ollama(text):
    try:
        translated_prompt, detected_language = translate_prompt_if_needed(
            f"{text} \n what are the key words in this text? Five keywords are enough"
        )

        payload = {
            "model": "llava", 
            "prompt": translated_prompt,
            "stream": True
        }

        full_response = call_ollama_api(payload)

        translated_response = translate_response_if_needed(full_response, detected_language)

        return translated_response.strip()
    
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

def get_summarize_with_ollama(text):
    try:
        translated_prompt, detected_language = translate_prompt_if_needed(
            f"{text} \n Can you summarize this text? Three sentences are enough"
        )

        payload = {
            "model": "llava", 
            "prompt": translated_prompt,
            "stream": True
        }

        full_response = call_ollama_api(payload)

        translated_response = translate_response_if_needed(full_response, detected_language)

        return translated_response.strip()
    
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

def get_discourse_with_ollama(text):
    try:
        translated_prompt, detected_language = translate_prompt_if_needed(
            f"{text} \n Can you do a discourse analysis of this paragraph?"
        )

        payload = {
            "model": "llava", 
            "prompt": translated_prompt,
            "stream": True
        }

        full_response = call_ollama_api(payload)

        translated_response = translate_response_if_needed(full_response, detected_language)

        return translated_response.strip()
    
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

def get_cleaned_frequency_analysis(text):
    try:
        words = text.lower().split()

        cleaned_words = [
            word.strip(string.punctuation)
            for word in words
            if word.strip(string.punctuation)
        ]

        frequency = {word: cleaned_words.count(word) for word in set(cleaned_words)}
        return frequency
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

def frequency_plot(frequency_dict, user_id=None):
    try:
        if not frequency_dict:
            return None

        sorted_items = sorted(frequency_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        words = [item[0] for item in sorted_items]
        counts = [item[1] for item in sorted_items]

        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(words, counts, color='skyblue', alpha=0.8)
        ax.set_title("Kelime Frekans Grafiği", fontsize=16, fontweight='bold')
        ax.set_xlabel("Kelimeler", fontsize=12)
        ax.set_ylabel("Frekans", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom', fontweight='bold')
        plt.tight_layout()

        # Kullanıcıya özel klasör
        if user_id:
            graph_dir = os.path.join('static', 'graphs', str(user_id))
        else:
            graph_dir = os.path.join('static', 'graphs')
        os.makedirs(graph_dir, exist_ok=True)
        filename = f"frequency_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(graph_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)
        # Sadece 'graphs/user_id/...' kısmını döndür
        rel_path = os.path.join('graphs', str(user_id), filename) if user_id else os.path.join('graphs', filename)
        return rel_path.replace("\\", "/")
    except Exception as e:
        print(f"[DEBUG] Grafik oluşturma hatası: {str(e)}")
        return None

def get_emotion_analysis_with_ollama(text):
    try:
        translated_prompt, detected_language = translate_prompt_if_needed(
            f"{text} \n Can you analyze the emotional tone and sentiment of this text? Please identify the dominant emotions (positive, negative, neutral) and explain the emotional elements you detect."
        )

        payload = {
            "model": "llava", 
            "prompt": translated_prompt,
            "stream": True
        }

        full_response = call_ollama_api(payload)

        translated_response = translate_response_if_needed(full_response, detected_language)

        return translated_response.strip()
    
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

TEXT_OPERATIONS = {
    'main_information': {
        'function': get_main_idea_with_ollama,
        'title': 'Metnin Ana Düşüncesi'
    },
    'keyword_extraction': {
        'function': get_keyword_with_ollama,
        'title': 'Anahtar Kelime Çıkarımı'
    },
    'summary': {
        'function': get_summarize_with_ollama,
        'title': 'Metin Özeti'
    },
    'discourse': {
        'function': get_discourse_with_ollama,
        'title': 'Metnin Söylem Analizi'
    },
    'frequency': {
        'function': get_cleaned_frequency_analysis,
        'title': 'Metnin Frekans Analizi'
    },
    'emotion': {
        'function': get_emotion_analysis_with_ollama,
        'title': 'Metnin Duygu Analizi'
    },
}

@app.route('/textual_operations', methods=['GET', 'POST'])
def textual_operations():
    if request.method == 'POST':
        text_content = request.form.get("text_content")
        operation = request.form.get("operation")
        user_id = is_user_logged_in()

        if not text_content or not operation:
            flash("Eksik veri gönderildi.", "file_danger")
            return redirect(url_for('textual_operations'))

        selected_operation = TEXT_OPERATIONS.get(operation)

        if not selected_operation:
            flash("Geçersiz işlem seçildi.", "file_danger")
            return redirect(url_for('textual_operations'))

        try:
            result = selected_operation['function'](text_content)
        except Exception as e:
            flash(f"İşlem hatası: {str(e)}", "file_danger")
            return redirect(url_for('textual_operations'))
        
        plot_img = None
        if operation == 'frequency' and isinstance(result, dict):
            if result:
                plot_img_path = frequency_plot(result, user_id)
                print(f"[DEBUG] Grafik dosya yolu: {plot_img_path}")
            else:
                flash("Hiç kelime bulunamadı.", "file_danger")
                return redirect(url_for('textual_operations'))
        else:
            plot_img_path = None

        session['textual_result'] = result
        session['textual_input'] = text_content
        session['textual_operation'] = selected_operation['title']
        session['plot_img_path'] = plot_img_path


        log_operation(is_user_logged_in(), operation, text_content, result, plot_img_path)
        return redirect(url_for('textual_operations'))
    else:
        result = session.get('textual_result', None)
        text_content = session.get('textual_input', '')
        operation_title = session.get('textual_operation', '')
        plot_img_path = session.get('plot_img_path', None)
        return render_template('textual_operations.html', result=result, text_content=text_content, operation_title=operation_title, plot_img_path=plot_img_path)

@app.route('/plot')
def plot():
    selected_values = session.get('selected_values', [])
    result = session.get('result', None)
    operation = session.get('operation', 'arithmetic')

    if not selected_values or result is None:
        return "Grafik oluşturulacak veri bulunamadı.", 400

    # Regresyon testi için sayısal değerlere dönüştür
    numeric_values = np.array(selected_values, dtype=float)

    img = create_dynamic_plot(numeric_values, operation, result)
    return send_file(img, mimetype='image/png')

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

@app.route('/operation_logs')
def operation_logs():
    user_id = session.get('user_id')

    if not user_id:
        flash("Kullanıcı giriş yapmamış", "file_danger")
        return redirect(url_for('home'))
    
    if 'selected_rows' in session:
        session.pop('selected_rows', None)

    # prompt varsa sıfırla
    if 'prompt' in session:
        session.pop('prompt', None)

    logs = get_operations_logs(user_id)
    return render_template('operation_logs.html', logs=logs)

@app.route('/delete_operation_log', methods=['POST'])
def delete_operation_log():
    user_id = is_user_logged_in()
    if not user_id:
            return jsonify({"success": False, "error": "Kullanıcı giriş yapmamış."}), 403
    
    data = request.json
    operation = data.get('operation')
    input_values = data.get('input_values')
    result = data.get('result')
    graph = data.get('graph')
    
    success = delete_operation_logs_db(user_id, operation, input_values, result)

    if graph:
            graph_path = os.path.join(os.getcwd(), graph.lstrip('/'))
            if os.path.exists(graph_path):
                os.remove(graph_path)
                print(f"Grafik dosyası silindi: {graph_path}")
            else:
                print(f"Grafik dosyası bulunamadı: {graph_path}")

    if success:
        return jsonify({"success": True, "message": "Log başarıyla silindi."})
    else:
        return jsonify({"success": False, "error": "Log silinirken bir hata oluştu."}), 500

@app.route('/ollama_chat', methods=['GET', 'POST'])
def ollama_chat():
    return render_template('ollama_chat.html') 

@app.route('/ollama_operation_chat', methods=['GET', 'POST'])
def ollama_operation_chat():
    if request.method == 'POST':
        selected_rows = request.json.get('selectedRows', [])
        if len(selected_rows) < 1:
            return jsonify({"success": False, "error": "Lütfen en az iki satır seçin!"}), 400
        
        session['selected_rows'] = selected_rows
        images, prompt = process_selected_rows(selected_rows)
        
        session['prompt'] = " ".join(prompt)
        session['images'] = images

        return jsonify({"success": True, "message": "İşlem başarıyla tamamlandı."})

    selected_rows = session.get('selected_rows', [])
    prompt = session.get('prompt', "")
    images = session.get('images', [])
    return render_template('ollama_operation_chat.html', selected_rows=selected_rows, prompt=prompt, images=images)

# !ollama_interact yardımcı fonksiyonlar
def translate_prompt_if_needed(user_input):
    translator = Translator()
    detected_language = translator.detect(user_input).lang
    print(f"[DEBUG] Algılanan dil: {detected_language}")

    if detected_language == 'tr':
        translated_input = translator.translate(user_input, src='tr', dest='en').text
        print(f"[DEBUG] Çevrilen prompt (Türkçe → İngilizce): {translated_input}")
    else:
        translated_input = user_input

    return translated_input, detected_language

def prepare_base64_image_payload(prompt, image_files):
    payload = {"model": "llava:latest", "prompt": f"User: {prompt}\nModel:"}
    base64_image = None
    merged_image_path = None

    if len(image_files) == 2:
        merged_image_path = merge_images(image_files[0], image_files[1])
        if not merged_image_path:
            raise Exception("Resimler birleştirilemedi")

        with open(merged_image_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')
        payload["images"] = [base64_image]
        print(f"[DEBUG] Resimler birleştirildi ve base64 formatına dönüştürüldü.")
    elif len(image_files) == 1:
        try:
            image = Image.open(image_files[0])
            image = image.convert("RGB")
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG")
            buffer.seek(0)
            base64_image = base64.b64encode(buffer.read()).decode('utf-8')
            payload["images"] = [base64_image]
            print(f"[DEBUG] Tek resim base64 formatına dönüştürüldü.")
        except Exception as e:
            raise Exception(f"Resim işleme hatası: {str(e)}")

    return payload, base64_image, merged_image_path

def call_ollama_api(payload):
    response = requests.post(
        'http://127.0.0.1:11434/api/generate',
        json=payload,
        headers={"Content-Type": "application/json"},
        stream=True,
    )

    if response.status_code != 200:
        raise Exception(f"Ollama API Hatası: {response.status_code} - {response.text}")

    full_response = ""
    for line in response.iter_lines():
        if line:
            try:
                json_line = json.loads(line.decode('utf-8'))
                full_response += json_line.get("response", "")
            except json.JSONDecodeError as e:
                print(f"JSON ayrıştırma hatası: {str(e)}")

    return full_response

def translate_response_if_needed(response, detected_language):
    if detected_language == 'tr':
        translator = Translator()
        translated_response = translator.translate(response, src='en', dest='tr').text
        print(f"[DEBUG] Çevrilen yanıt (İngilizce → Türkçe): {translated_response}")
        return translated_response
    return response

def append_to_chat_history(user_input, translated_response):
    session['chat_history'].append(f"Kullanıcı: {user_input}")
    session['chat_history'].append(f"Model: {translated_response}")

def build_final_response(translated_response, merged_image_path, uploaded_image_paths):
    return jsonify({
        "success": True,
        "response": translated_response,
        "merged_image_url": f"/{merged_image_path}" if merged_image_path else None,
        "uploaded_images": [f"/{path}" for path in uploaded_image_paths]
    })

@app.route('/ollama', methods=['POST'])
def ollama_interact():
    user_id = is_user_logged_in()
    user_input = request.form.get('input', '')
    image_files = request.files.getlist('image')

    uploaded_image_paths = save_uploaded_images(image_files)
    session['chat_history'] = []

    translated_input, detected_language = translate_prompt_if_needed(user_input)
    payload, base64_image, merged_image_path = prepare_base64_image_payload(translated_input, image_files)

    try:
        full_response = call_ollama_api(payload)
        translated_response = translate_response_if_needed(full_response, detected_language)

        append_to_chat_history(user_input, translated_response)
        log_llama_chat(user_id, user_input, translated_response, image_data=base64_image)

        return build_final_response(translated_response, merged_image_path, uploaded_image_paths)
    except Exception as e:
        print(f"[DEBUG] Hata: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/ollama_logs')
def ollama_logs():
    user_id = session.get('user_id')

    if not user_id:
        flash("Kullanıcı giriş yapmamış", "file_danger")
        return redirect(url_for('home'))
    
    if 'selected_rows' in session:
        session.pop('selected_rows', None)

    # prompt  varsa sıfırla
    if 'prompt' in session:
        session.pop('prompt', None)

    logs = get_log_llama(user_id)
    return render_template('ollama_logs.html', logs=logs)
@app.route('/download_log_pdf')
def download_log_pdf():
    operation = unidecode(request.args.get('operation', ''))
    input_values = unidecode(request.args.get('input_values', ''))
    result = unidecode(request.args.get('result', ''))
    graph_path = request.args.get('graph', '')

    pdf = FPDF()
    pdf.add_page()

    font_path = os.path.join('static', 'fonts', 'DejaVuSans.ttf')
    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.set_font('DejaVu', '', 12)

    # multi_cell ile otomatik satır sonu
    pdf.multi_cell(0, 8, txt=f"Operation: {operation}")
    pdf.ln(2)
    pdf.multi_cell(0, 8, txt=f"Input Values: {input_values}")
    pdf.ln(2)
    pdf.multi_cell(0, 8, txt=f"Result: {result}")
    pdf.ln(5)

    # Resim ekleme (önceki kodun gibi)
    if graph_path:
        full_path = os.path.join('static', graph_path.replace('\\', '/').replace('static/', ''))
        if os.path.exists(full_path):
            y = pdf.get_y()
            try:
                pdf.image(full_path, x=10, y=y, w=150)
                # resimden sonra satırı ilerlet
                pdf.set_y(y + 60 + 10)
            except RuntimeError:
                pdf.multi_cell(0, 8, txt="Resim eklenemedi.")
        else:
            pdf.multi_cell(0, 8, txt="Görsel bulunamadı.")

    buffer = io.BytesIO()
    pdf.output(buffer)
    pdf_bytes = buffer.getvalue()

    response = make_response(pdf_bytes)
    response.headers.set('Content-Type', 'application/pdf')
    response.headers.set('Content-Disposition', 'attachment', filename='log.pdf')
    return response

    operation = request.args.get('operation', '')
    input_values = request.args.get('input_values', '')
    result = request.args.get('result', '')
    graph_path = request.args.get('graph', '')

    pdf = FPDF()
    pdf.add_page()

    # Türkçe karakterler için font
    font_path = os.path.join('static', 'fonts', 'DejaVuSans.ttf')
    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.set_font('DejaVu', '', 12)

    # Satır atlamaları otomatik işlenir
    pdf.multi_cell(0, 10, txt=f"Operation:\n{operation}")
    pdf.ln(2)
    pdf.multi_cell(0, 10, txt=f"Input Values:\n{input_values}")
    pdf.ln(2)
    pdf.multi_cell(0, 10, txt=f"Result:\n{result}")
    pdf.ln(5)

    # Grafik varsa ekle
    if graph_path and os.path.exists(graph_path):
        pdf.image(graph_path, x=10, w=190)  # genişliği sayfaya göre ayarla

    # PDF’i geçici dosyaya kaydet
    output_path = "output_log.pdf"
    pdf.output(output_path)

    return send_file(output_path, as_attachment=True)
    operation = unidecode(request.args.get('operation', ''))
    input_values = unidecode(request.args.get('input_values', ''))
    result = unidecode(request.args.get('result', ''))
    graph_path = request.args.get('graph', '')

    pdf = FPDF()
    pdf.add_page()

    # Font ayarı
    font_path = os.path.join('static', 'fonts', 'DejaVuSans.ttf')
    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.set_font('DejaVu', '', 12)

    # İçerik yazımı
    pdf.multi_cell(0, 10, txt=f"Operation:\n{operation}")
    pdf.ln(3)

    pdf.multi_cell(0, 10, txt=f"Input Values:\n{input_values}")
    pdf.ln(3)

    pdf.multi_cell(0, 10, txt=f"Result:\n{result}")
    pdf.ln(5)

    # Grafik varsa ekle
    if graph_path and os.path.exists(graph_path):
        pdf.image(graph_path, x=10, y=pdf.get_y(), w=pdf.w - 20)
    
    # # PDF dosyasını kaydet
    # output_path = 'output.pdf'
    # pdf.output(output_path)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
