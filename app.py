from flask import Flask, render_template, request, redirect, url_for, flash
from db import init_db, sign_up, sign_in, save_file
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'

# MSSQL DB Settings
DATABASE_CONFIG = {
    'DRIVER': '{ODBC Driver 17 for SQL Server}',
    'SERVER': '10.60.124.192',  # Server IP
    'DATABASE': 'deneme',
    'UID': 'sa',  # Kullanıcı adı
    'PWD': 'Deneme'  # Şifre
}

# MSSQL bağlantısını başlatmak için app.context kullanımı
with app.app_context():
    init_db(DATABASE_CONFIG)  # Veritabanı bağlantısını başlatır.

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def sign_in_route():
    email = request.form['e-mail']
    password = request.form['sifre']
    user = sign_in(email, password)
    if user:
        flash("Giriş Başarılı", "success") 
        return redirect(url_for('main_page')) 
    else:
        flash("Giriş Başarısız", "danger")
        return redirect(url_for('home')) 

@app.route('/register')
def register():
    return render_template('register.html')

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

@app.route('/main_page')
def main_page():
    return render_template('main_page.html')

if __name__ == '__main__':
    app.run(debug=True)
