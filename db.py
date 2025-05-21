from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb
import pandas as pd
import io
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document

mysql = MySQL()

# ! Yardımcı Fonksiyonlar
def _read_excel(byte_data):
    try:
        excel_data = pd.read_excel(io.BytesIO(byte_data), engine='openpyxl')
        excel_data.columns = [str(col) if col and 'Unnamed' not in str(col) else '' for col in excel_data.columns]
        return excel_data if not excel_data.empty else None
    except Exception as e:
        print(f"Excel dosyası okuma hatası: {str(e)}")
        return None

def _read_csv(byte_data):
    try:
        csv_data = pd.read_csv(io.BytesIO(byte_data))
        csv_data.columns = [str(col) if col and 'Unnamed' not in str(col) else '' for col in csv_data.columns]
        return csv_data if not csv_data.empty else None
    except Exception as e:
        print(f"CSV dosyası okuma hatası: {str(e)}")
        return None

def _delete_column(file_content, user_id, file_name, update):
    column_name = update['column_name']
    if column_name in file_content.columns:
        file_content.drop(columns=[column_name], inplace=True)
        log_change(user_id, file_name, "delete_column", column_name=column_name)

def _add_column(file_content, user_id, file_name, update):
    new_column_name = update['column_name']
    file_content[new_column_name] = ''
    log_change(user_id, file_name, "add_column", column_name=new_column_name)

def _delete_row(file_content, user_id, file_name, update):
    row_index = update['row_index']
    if 0 <= row_index < len(file_content):
        file_content.drop(index=row_index, inplace=True)
        file_content.reset_index(drop=True, inplace=True)
        log_change(user_id, file_name, "delete_row", row_index=row_index)

def _add_row(file_content, user_id, file_name, update):
    row_index = update.get('row_index')
    columns = update.get('columns', [])
    new_row = {col['column_name']: col['value'] for col in columns}
    file_content.loc[len(file_content)] = new_row
    log_change(user_id, file_name, "add_row", row_index=row_index)

def _update_cell(file_content, user_id, file_name, update):
    row_index = int(update['row_index'])
    column_name = update['column_name']
    new_value = update['new_value']

    if row_index < len(file_content) and column_name in file_content.columns:
        old_value = file_content.at[row_index, column_name]
        file_content.at[row_index, column_name] = new_value
        log_change(user_id, file_name, "update_cell", column_name=column_name, row_index=row_index, old_value=old_value, new_value=new_value)

def _update_text(file_content, user_id, file_name, update):
    new_content = update['content']
    try:
        # print(f"[DEBUG] Güncellenen içerik (önceki): {file_content}")
        if isinstance(file_content, bytes):
            updated_content = new_content
        else: 
            updated_content = new_content.encode('utf-8')
        # print(f"[DEBUG] Güncellenen içerik (sonraki): {updated_content}")
        return updated_content
    except Exception as e:
        print(f"Metin dosyası güncellenirken hata oluştu: {str(e)}")
        return file_content

def create_pdf_from_text(text):
    output = io.BytesIO()
    c = canvas.Canvas(output, pagesize=letter)

    font_path = os.path.join("static", "fonts", "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
    c.setFont("DejaVuSans", 12)

    y = 750
    for line in text.splitlines():
        c.drawString(72, y, line)
        y -= 15
        if y < 72:
            c.showPage()
            c.setFont("DejaVuSans", 12)
            y = 750

    c.save()
    return output.getvalue()

def create_docx_from_text(text):
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)

    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()

def _save_file_content(user_id, file_name, file_content, file_type):
    try:
        output = None

        if file_type == 'xlsx':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                file_content.to_excel(writer, index=False)
            file_byte_data = output.getvalue()
        elif file_type == 'csv':
            output = io.BytesIO()
            file_content.to_csv(output, index=False, encoding='utf-8')
            file_byte_data = output.getvalue()
        elif file_type == 'pdf':
            if isinstance(file_content, str):
                print("[DEBUG] PDF metin olarak geldi, yeni PDF oluşturulacak.")
                file_byte_data = create_pdf_from_text(file_content)
            else:
                return "PDF içeriği metin olarak bekleniyor."
        elif file_type == 'docx':
            print("[DEBUG] DOCX dosyası işleniyor")
            if isinstance(file_content, str):
                file_byte_data = create_docx_from_text(file_content)
                print(f"[DEBUG] Yeni DOCX oluşturuldu. Uzunluk: {len(file_byte_data)}")
            else:
                print("[HATA] DOCX için yalnızca metin içeriği bekleniyor.")
                return "DOCX içeriği metin olarak bekleniyor."
        else:
            file_byte_data = file_content

        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE user_files SET file_content = %s WHERE user_id = %s AND file_name = %s",
            (file_byte_data, user_id, file_name)
        )
        mysql.connection.commit()
        cur.close()

        print(f"Dosya başarıyla güncellendi: {file_name}")
    except Exception as e:
        print(f"Dosya kaydedilirken hata oluştu: {str(e)}")

# ! Veritabanı İşlemleri
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

        # log_table tablosu
        cur.execute("""
        CREATE TABLE IF NOT EXISTS log_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            action_type VARCHAR(50) NOT NULL, 
            column_name VARCHAR(255),
            row_index INT,
            old_value TEXT,
            new_value TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        # operation_logs tablosu
        cur.execute("""
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                operation VARCHAR(50) NOT NULL,
                input_values TEXT NOT NULL,
                result TEXT NOT NULL,
                graph_path VARCHAR(255) DEFAULT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # llama_logs
        cur.execute("""
            CREATE TABLE IF NOT EXISTS llama_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                question TEXT NOT NULL, 
                answer TEXT NOT NULL,
                image_data LONGBLOB DEFAULT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
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

    if not file_data or not file_data[0]:
        print("Dosya içeriği bulunamadı veya boş.")
        return None

    byte_data = file_data[0]
    
    if file_type == 'xlsx':
        return _read_excel(byte_data)
    elif file_type == 'csv':
        return _read_csv(byte_data)
    elif file_type in ['txt', 'pdf', 'docx']:
        return byte_data
    else:
        print(f"Desteklenmeyen dosya türü: {file_type}")
        return None

def log_change(user_id, file_name, action_type, column_name=None, row_index=None, old_value=None, new_value=None):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO log_table (user_id, file_name, action_type, column_name, row_index, old_value, new_value, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (user_id, file_name, action_type, column_name, row_index, old_value, new_value))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print(f"Loglama hatası: {str(e)}")

def get_logs(file_name, user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, action_type, column_name, row_index, old_value, new_value, timestamp FROM log_table
        WHERE file_name = %s AND user_id = %s
        ORDER BY timestamp DESC
    """, (file_name, user_id))
    logs = cur.fetchall()
    cur.close()
    return logs

def update_table_data(user_id, file_name, updated_data):
    file_type = file_name.rsplit('.', 1)[1].lower()
    file_content = get_file_data(user_id, file_name, file_type)
    
    if isinstance(file_content, str):
        return file_content
    
    try:
        for update in updated_data:
            if 'delete_column' in update:
                _delete_column(file_content, user_id, file_name, update)
                new_file_content = file_content
            
            elif 'add_column' in update:
                _add_column(file_content, user_id, file_name, update)
                new_file_content = file_content
                
            elif 'delete_row' in update:
                _delete_row(file_content, user_id, file_name, update)
                new_file_content = file_content
                
            elif 'is_new_row' in update:
                _add_row(file_content, user_id, file_name, update)
                new_file_content = file_content

            elif 'row_index' in update and 'column_name' in update:
                _update_cell(file_content, user_id, file_name, update)
                new_file_content = file_content
                
            elif 'update_text' in update:
                new_file_content = _update_text(file_content, user_id, file_name, update)

        _save_file_content(user_id, file_name, new_file_content, file_type)
        return True
    except Exception as e:
        print(f"Güncelleme hatası: {str(e)}")
        return f"Güncelleme hatası: {str(e)}"    
           
def rollback_change(user_id, file_name, log_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT action_type, column_name, row_index, old_value
            FROM log_table
            WHERE id = %s AND user_id = %s AND file_name = %s
        """, (log_id, user_id, file_name))
        log_entry = cur.fetchone()
        cur.close()

        if not log_entry:
            return "Log kaydı bulunamadı."

        action_type, column_name, row_index, old_value = log_entry

        # Dosya içeriğini al
        file_type = file_name.rsplit('.', 1)[1].lower()
        file_content = get_file_data(user_id, file_name, file_type)

        if isinstance(file_content, str):
            return file_content 

        # İşleme göre geri alma
        if action_type == "update_cell":
            if column_name in file_content.columns and 0 <= row_index < len(file_content):
                file_content.loc[row_index, column_name] = old_value

        # Silinen satırı geri eklemek mümkün değil (log'da satırın tüm değerleri yok)
        elif action_type == "delete_row":
            return "Satır silme işlemi geri alınamaz."

        # Eklenen satırı sil
        elif action_type == "add_row":
            file_content = file_content.drop(index=row_index).reset_index(drop=True)

        # Silinen sütunu geri eklemek mümkün değil (log'da sütunun tüm değerleri yok)
        elif action_type == "delete_column":
            return "Sütun silme işlemi geri alınamaz."

        # Eklenen sütunu sil
        elif action_type == "add_column":
            if column_name in file_content.columns:
                file_content = file_content.drop(columns=[column_name])

        # Güncellenmiş dosya içeriğini kaydet
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
        
        # geri alınan işlemi logdan silme
        cur.execute("DELETE FROM log_table WHERE id = %s AND user_id = %s AND file_name = %s",
                    (log_id, user_id, file_name))
        mysql.connection.commit()
        cur.close()

        return "Değişiklik başarıyla geri alındı."
    except Exception as e:
        print(f"Geri alma hatası: {str(e)}")
        return f"Geri alma hatası: {str(e)}"

def log_operation(user_id, operation, input_values, result, graph_path=None):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO operation_logs (user_id, operation, input_values, result, graph_path, timestamp)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (user_id, operation, str(input_values), str(result), graph_path))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print(f"İşlem loglama hatası: {str(e)}")

def get_operations_logs(user_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT operation, input_values, result, timestamp, graph_path
            FROM operation_logs
            WHERE user_id = %s
            ORDER BY timestamp DESC
        """, (user_id,))
        logs = cur.fetchall()
        cur.close()
        return logs
    except Exception as e:
        print(f"Operation logs alınırken hata oluştu: {str(e)}")
        return []

def delete_operation_logs_db(user_id, operation, input_values, result, graph):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM operation_logs WHERE user_id = %s AND operation = %s AND input_values = %s AND result = %s AND graph_path = %s", (user_id, operation, input_values, result, graph))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Operation log silinirken hata oluştu: {str(e)}")
        return False

def log_llama_chat(user_id, question, answer, image_data=None):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO llama_logs (user_id, question, answer, image_data)
            VALUES (%s, %s, %s, %s)
        """, (user_id, question, answer, image_data))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print(f"Llama sohbeti loglanırken hata oluştu: {str(e)}")

def get_log_llama(user_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT question, answer, image_data, timestamp
            FROM llama_logs
            WHERE user_id = %s
            ORDER BY timestamp DESC
        """, (user_id,))
        logs = cur.fetchall()
        cur.close()

        formatted_logs = []
        for log in logs:
            question, answer, image_data, timestamp = log
            if image_data:
                image_data = image_data.decode('utf-8')  # bytes -> string
            formatted_logs.append((question, answer, image_data, timestamp))

        return formatted_logs
    except Exception as e:
        print(f"Ollama logs alınırken hata oluştu: {str(e)}")
        return []
