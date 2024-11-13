import os
from flask import Flask, render_template, request, redirect, url_for, flash
from db import init_db, sign_up, sign_in
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = 'gizli_anahtar'

# ? DB Settings 
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'root')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'bitirme')

init_db(app)

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
    if request.method == 'POST':
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
