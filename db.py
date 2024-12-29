from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb
import pandas as pd
import io
import numpy as np

mysql = MySQL()

def init_db(app):
    global mysql
    mysql = MySQL(app)

def create_database():
    try:
        conn = MySQLdb.connect(
            host='localhost',
            user='root',       
            passwd='root'     
        )
        cur = conn.cursor()

        cur.execute("CREATE DATABASE IF NOT EXISTS bitirme")
        print("Veritabanı başarıyla oluşturuldu veya zaten mevcut.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Veritabanı oluşturulurken hata oluştu: {e}")

def create_tables():
    try:
        conn = mysql.connect
        conn.select_db('bitirme') 
        cur = conn.cursor()

        # users tablosu
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
        """)

        # user_files tablosu
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            file_content LONGBLOB,
            FOREIGN KEY (user_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_turkish_ci
        """)

        print("Tablolar başarıyla oluşturuldu veya zaten mevcut.")
        cur.close()
        conn.commit()
    except Exception as e:
        print(f"Tablolar oluşturulurken hata oluştu: {e}")

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

def update_table_data(user_id, file_name, updated_data):
    file_type = file_name.rsplit('.', 1)[1].lower()
    file_content = get_file_data(user_id, file_name, file_type)
    
    if isinstance(file_content, str):
        return file_content
    
    try:
        for update in updated_data:
            if 'delete_row' in update:  # Satır silme
                row_index = update['row_index']
                file_content = file_content.drop(index=row_index).reset_index(drop=True)
                
            elif 'is_new_row' in update:  # Yeni satır ekleme
                # Boş bir DataFrame satırı oluştur
                empty_row = pd.Series([''] * len(file_content.columns), index=file_content.columns)
                
                # Yeni satırı DataFrame'e ekle
                file_content = pd.concat([file_content, pd.DataFrame([empty_row])], ignore_index=True)
                
                # NaN değerleri boş string ile değiştir
                file_content = file_content.fillna('')
                
            elif 'row_index' in update and 'column_name' in update:  # Mevcut satır güncelleme
                row_index = int(update['row_index'])
                column_name = update['column_name']  
                new_value = update['new_value'] 

                if column_name in file_content.columns:
                    file_content.loc[row_index, column_name] = new_value
                    # Güncellemeden sonra NaN değerleri boş string yap
                    file_content = file_content.fillna('')
                else:
                    print(f"Geçersiz sütun adı: {column_name}")

            elif 'column_name' in update:  # Sütun başlığı güncellemesi
                column_name = update['column_name']  
                new_value = update['new_value']  

                if column_name in file_content.columns:
                    file_content.rename(columns={column_name: new_value}, inplace=True)
                else:
                    print(f"Geçersiz sütun adı: {column_name}")

        # Son bir kez daha NaN değerleri kontrol et
        file_content = file_content.fillna('')

        output = io.BytesIO()  
        if file_type == 'xlsx':  
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                file_content.to_excel(writer, index=False)
        elif file_type == 'csv':  
            file_content.to_csv(output, index=False, encoding='utf-8') 

        file_byte_data = output.getvalue()

        cur = mysql.connection.cursor() 
        cur.execute("UPDATE user_files SET file_content = %s WHERE user_id = %s AND file_name = %s",
                    (file_byte_data, user_id, file_name)) 
        mysql.connection.commit()  
        cur.close()  
        return True
        
    except Exception as e:
        print(f"Güncelleme hatası: {str(e)}")
        return f"Güncelleme hatası: {str(e)}"








