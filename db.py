from flask import current_app
from flask_mysqldb import MySQL

mysql = None

def init_db(app):
    global mysql
    mysql = MySQL(app)
    with app.app_context():
        create_database_if_not_exists()
        create_users_table()

def create_database_if_not_exists():
    cur = mysql.connection.cursor()
    cur.execute("CREATE SCHEMA IF NOT EXISTS bitirme")  
    mysql.connection.commit()
    cur.close()

def create_users_table():
    with current_app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("USE bitirme")
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
        mysql.connection.commit()
        cur.close()

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