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

def uptade_table_data(user_id, file_name, updated_data, file_type='xlsx'):
    # Mevcut dosya içeriğini al
    file_type = file_name.rsplit('.', 1)[1].lower()
    file_content = get_file_data(user_id, file_name, file_type)
    
    if isinstance(file_content, str):  # Hata mesajı geldi mi?
        return file_content

    # Güncellenen verileri işle
    for update in updated_data:
        row_index = int(update['row_index'])  # Satır indexini al
        column_name = update['column_name']  # Sütun adını al
        new_value = update['new_value']  # Yeni değeri al

        # Veriyi güncelle
        if row_index < len(file_content) and column_name in file_content.columns:
            file_content.at[row_index, column_name] = new_value
        else:
            return "Geçersiz satır veya sütun adı."

    # Güncellenmiş veriyi byte formatına çevir
    output = io.BytesIO()
    if file_type == 'xlsx':
        file_content.to_excel(output, index=False, engine='openpyxl')
    elif file_type == 'csv':
        file_content.to_csv(output, index=False, encoding='utf-8')

    # Veriyi veritabanına kaydet
    file_byte_data = output.getvalue()

    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE user_files SET file_content = %s WHERE user_id = %s AND file_name = %s",
                    (file_byte_data, user_id, file_name))
    except Exception as e:
        return f"Dosya güncelleme hatası: {str(e)}"

    mysql.connection.commit()
    cur.close()
    return "Dosya başarıyla güncellendi."



