from flask_mysqldb import MySQL
from datetime import datetime
import pandas as pd
import io

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

def save_files (user_id ,file_name, file_content):
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO user_files (user_id, file_name, uploaded_at, file_content) VALUES (%s, %s, %s, %s)",
        (user_id, file_name, datetime.now(), file_content)
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

def get_file_data(user_id, file_name, file_type=None):
    cur = mysql.connection.cursor()
    cur.execute("SELECT file_content FROM user_files WHERE user_id = %s AND file_name = %s",
        (user_id, file_name)
    )
    file_data = cur.fetchone()
    cur.close()

    if file_data and file_data[0]:
        byte_data = file_data[0]

        if file_type == 'xlsx':
            try:
                excel_data = pd.read_excel(io.BytesIO(byte_data), engine='openpyxl')
                excel_data.columns = ['' if 'Unnamed' in col else col for col in excel_data.columns]
                if not excel_data.empty:
                    return excel_data
                else:
                    return "Excel dosyası boş."
            except Exception as e:
                return f"Excel dosyası okuma hatası: {e}"

        elif file_type == 'csv':
            try:
                csv_data = pd.read_csv(io.BytesIO(byte_data))
                csv_data.columns = ['' if 'Unnamed' in col else col for col in csv_data.columns]
                if not csv_data.empty:
                    return csv_data
                else:
                    return "CSV dosyası boş."
            except Exception as e:
                return f"CSV dosyası okuma hatası: {e}"

    return None

