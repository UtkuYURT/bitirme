import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from io import BytesIO
from db import init_db, sign_up, sign_in, save_file
from dotenv import load_dotenv
import pyodbc
from flask import session

load_dotenv()

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'

# MSSQL DB Settings
DATABASE_CONFIG = {
    'DRIVER': '{ODBC Driver 17 for SQL Server}',
    'SERVER': '192.168.1.168',  # Server IP
    'DATABASE': 'deneme',
    'UID': 'sa',  # Kullanıcı adı
    'PWD': 'Deneme'  # Şifre
}

# MSSQL bağlantısını başlatmak için app.context kullanımı
with app.app_context():
    init_db(DATABASE_CONFIG)  # Veritabanı bağlantısını başlatır.


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_latest_file_from_db(db_config, user_id):
    """Giriş yapan kullanıcının yüklediği son dosyayı getirir."""
    try:
        conn = pyodbc.connect(
            f'DRIVER={db_config["DRIVER"]};'
            f'SERVER={db_config["SERVER"]};'
            f'DATABASE={db_config["DATABASE"]};'
            f'UID={db_config["UID"]};'
            f'PWD={db_config["PWD"]}'
        )
        cursor = conn.cursor()

        # Kullanıcının yüklediği son dosyayı getiren sorgu
        query = """
        SELECT TOP 1 filename, filedata
        FROM files
        WHERE CreateUserId = ? AND filename LIKE '%.pdf'
        ORDER BY Id DESC
        """
        cursor.execute(query, (user_id,))
        file = cursor.fetchone()

        conn.close()

        if file:
            return {'filename': file[0], 'filedata': file[1]}
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# PDF dosyasını tarayıcıda gösterme route'u
@app.route('/get_latest_file')
def get_latest_file():
    user_id = session.get('user_id')  # Kullanıcı ID'sini al
    last_file = get_latest_file_from_db(DATABASE_CONFIG, user_id)  # Veritabanından son dosyayı al

    if last_file:
        # PDF dosyasını BytesIO ile sararak gönder
        return send_file(BytesIO(last_file['filedata']),
                         mimetype='application/pdf',  # PDF mimetype'ı
                         as_attachment=False,  # Dosya tarayıcıda görüntülenecek, indirilmeyecek
                         download_name=last_file['filename'])  # Dosya adını belirt
    else:
        flash("Henüz bir dosya yüklenmedi.", "danger")
        return redirect(url_for('main_page'))

# Dosya yükleme ve kaydetme
@app.route('/upload', methods=['GET', 'POST'])
def upload_file_route():
    if request.method == 'POST':
        file = request.files.get('file')

        if not file or file.filename == '':
            flash('Dosya seçilmedi', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = file.filename
            filedata = file.read()  # Dosyayı binary olarak oku

            # Kullanıcı ID'sini session'dan al
            user_id = session.get('user_id')
            if not user_id:
                flash('Giriş yapmalısınız!', 'danger')
                return redirect(url_for('home'))

            # Dosyayı kaydet ve kullanıcı ID'sini ekle
            save_file(filename, filedata, user_id)
            flash('Dosya başarıyla yüklendi', 'success')
            return redirect(url_for('main_page'))
        else:
            flash('İzin verilmeyen dosya türü', 'danger')
            return redirect(request.url)

    return render_template('main_page.html')

@app.route('/register', methods=['POST'])
def sign_up_route():
    email = request.form['e-mail']
    password1 = request.form['sifre']
    password2 = request.form['sifre2']
    if password1 == password2:
        sign_up(email, password1)
        flash("Kayıt Başarılı", "success")
        return redirect(url_for('home')) 
    else:
        flash("Kayıt Başarısız", "danger")
        return redirect(url_for('register'))

# Ana sayfa route'u
@app.route('/main_page')
def main_page():
    user_id = session.get('user_id')  # Kullanıcı ID'sini al
    last_file = get_latest_file_from_db(DATABASE_CONFIG, user_id)  # Son yüklenen dosya bilgisini al
    return render_template('main_page.html', last_file=last_file)  # Dosya bilgisini şablona gönder


# Anasayfa route'u (giriş)
@app.route('/')
def home():
    return render_template('index.html')


# Kayıt route'u
@app.route('/register')
def register():
    return render_template('register.html')

# Giriş işlemi
@app.route('/', methods=['POST'])


@app.route('/sign_up', methods=['POST'])
def sign_in_route():
    email = request.form['e-mail']
    password = request.form['sifre']
    user = sign_in(email, password)
    if user:
        session['user_id'] = user[0]  # Kullanıcı ID'sini session'a kaydet
        flash("Giriş Başarılı", "success")
        return redirect(url_for('main_page'))
    else:
        flash("Giriş Başarısız", "danger")
        return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)