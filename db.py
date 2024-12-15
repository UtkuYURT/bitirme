from flask_mysqldb import MySQL
from datetime import datetime 

mysql = None

def init_db(app):
    global mysql
    mysql = MySQL(app)

def sign_in(email, password):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    cur.close()
    return user

def sign_up(email, password):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
    mysql.connection.commit()
    cur.close()

def save_files (user_id ,file_name):
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO user_files (user_id, file_name, uploaded_at) VALUES (%s, %s, %s)",
        (user_id, file_name, datetime.now())
    )
    mysql.connection.commit()
    cur.close()

def get_files (user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT file_name, uploaded_at FROM user_files WHERE user_id = %s", (user_id,))
    files = cur.fetchall()
    cur.close()
    return files

def delete_files (user_id, file_name):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM user_files WHERE user_id = %s and file_name = %s", (user_id, file_name))
    mysql.connection.commit()
    cur.close()

