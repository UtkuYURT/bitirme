from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import init_db, sign_up, sign_in, save_files, get_files

app = Flask(__name__)

app.secret_key = 'gizli_anahtar'

# ? DB Settings 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'bitirme'

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
            session['user_id'] = user[0]
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
    return render_template('main_page.html', show_sidebar=False)

@app.route('/file_operations')
def file_operations():
    user_id = session.get('user_id')
    if user_id:
        files = get_files(user_id) 
        return render_template("file_operations.html", files=files)
    else:
        flash("Kullanıcı bulunamadı", "danger")
        return redirect(url_for("/"))

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if user_id:
            file = request.files.get('file')
            if file or file.filename != "":
                filename = file.filename
                save_files(user_id ,filename)
                return redirect(url_for('file_operations'))
            else:
                flash("Dosya seçilemedi", "danger");
                return redirect(url_for('file_operations'))
        else:
            flash("Kullanıcı bulunamadı", "danger")
            return redirect(url_for("/"))

if __name__ == '__main__':
    app.run(debug=True)
