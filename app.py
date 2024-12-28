from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from db import init_db, sign_up, sign_in, save_files, get_files, delete_files, get_file_data, uptade_table_data, initialize_database
import pandas as pd
import os

app = Flask(__name__)

app.secret_key = 'gizli_anahtar'

# ? DB Settings 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'bitirme'

init_db(app)

with app.app_context():
    initialize_database()

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
        else:
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
        else:
            flash("Kayıt Başarısız", "login_danger")
            return redirect(url_for('register'))

@app.route('/file_operations')
def file_operations():
    user_id = session.get('user_id')
    if user_id:
        files = get_files(user_id) 
        return render_template("file_operations.html", files=files)
    else:
        flash("Kullanıcı bulunamadı", "file_danger")
        return redirect(url_for("/"))

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if user_id:
            file = request.files.get('file')
            if file and allowed_file(file.filename): 
                filename = file.filename
                file_content = file.read()
                save_files(user_id, filename, file_content)
                flash("Dosya başarıyla kaydedildi", "file_success")
                return redirect(url_for('file_operations'))
            else:
                flash("Geçersiz dosya türü.", "file_danger")
                return redirect(url_for('file_operations'))
        else:
            flash("Kullanıcı bulunamadı", "file_danger")
            return redirect(url_for("/"))

@app.route('/delete_file', methods=['POST'])
def delete_file():
    if request.method == 'POST':
        user_id = session.get('user_id')
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

def generate_editable_table(df):
    table_html = '<table class="table table-bordered table-hover" id="editable-table">'
    
    # Başlıkları ekle
    table_html += '<thead><tr>'
    for col in df.columns:
        table_html += f'<th>{col}</th>'
    table_html += '</tr></thead>'
    
    # Satırları ekle
    table_html += '<tbody>'
    for i, row in df.iterrows():
        table_html += '<tr>'
        for col in df.columns:
            # contenteditable özelliği ile hücreyi düzenlenebilir hale getir
            table_html += f'<td contenteditable="true" data-column="{col}" data-row="{i}">{row[col]}</td>'
        table_html += '</tr>'
    table_html += '</tbody></table>'
    
    return table_html

@app.route('/main_page')
def main_page():
    # Burada, dosya içeriğini ve diğer verileri yükleyebilirsiniz
    return render_template('main_page.html')

@app.route('/main_page/<file_name>', methods=['GET', 'POST'])
def view_file(file_name):
    user_id = session.get('user_id')

    if not user_id:
        flash("Kullanıcı giriş yapmamış", "file_danger")
        return redirect(url_for('login'))  # Kullanıcıyı giriş sayfasına yönlendir

    if request.method == 'GET':
        file_extension = os.path.splitext(file_name)[1].lower()

        if file_extension == '.xlsx':
            file_content = get_file_data(user_id, file_name, file_type='xlsx')
        else:
            file_content = get_file_data(user_id, file_name, file_type='csv')

        if file_content is not None and isinstance(file_content, pd.DataFrame):
            if not file_content.empty:
                table_html = generate_editable_table(file_content)
                return render_template('main_page.html', file_name=file_name, content=table_html)
            else:
                flash("Dosya boş", "file_danger")
        else:
            flash("Dosya bulunamadı veya içerik mevcut değil", "file_danger")
        
        return redirect(url_for('main_page'))  # Boş dosya durumu için ana sayfaya yönlendirme

    else:
        data = request.get_json()
        updated_data = data.get('updated_data')

        try:
            uptade_table_data(user_id, file_name, updated_data)  # Veritabanını güncelle
            flash("Dosya kaydedilmesi başarılı", "file_success")
            return jsonify({"success": True, "message": "Veriler başarıyla güncellendi."})
        except Exception as e:
            flash("Dosya kaydedilemedi", "file_danger")
            return jsonify({"success": False, "message": f"Hata: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
