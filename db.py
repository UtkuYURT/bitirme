from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb
import pandas as pd
import io

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
            if 'delete_column' in update:  # Sütun silme
                column_name = update['column_name']
                if column_name in file_content.columns:
                    file_content = file_content.drop(columns=[column_name])
                    log_change(user_id, file_name, "delete_column", column_name=column_name)
            
            elif 'add_column' in update:
                new_column_name = update['column_name']
                file_content[new_column_name] = ''
                log_change(user_id, file_name, "add_column", column_name=new_column_name)
                
            elif 'delete_row' in update:
                row_index = update['row_index']
                if 0 <= row_index < len(file_content):
                    file_content = file_content.drop(index=row_index).reset_index(drop=True)
                    log_change(user_id, file_name, "delete_row", row_index=row_index)
                
            elif 'is_new_row' in update:
                row_index = update.get('row_index')
                columns = update.get('columns', [])

                new_row = {col['column_name']: col['value'] for col in columns}

                file_content = pd.concat([file_content, pd.DataFrame([new_row])], ignore_index=True)
                file_content = file_content.fillna('')

                log_change(user_id, file_name, "add_row", row_index=len(file_content) - 1)
                
            elif 'row_index' in update and 'column_name' in update:
                row_index = int(update['row_index'])
                column_name = update['column_name']
                new_value = update['new_value']

                old_value = None
                if row_index < len(file_content) and column_name in file_content.columns:
                    old_value = file_content.loc[row_index, column_name]

                # Sayısal değer kontrolü ve dönüşümü
                try:
                    if new_value.strip().isdigit():  # Tam sayı kontrolü
                        new_value = int(new_value)
                    elif new_value.replace('.', '', 1).isdigit():  # Ondalık sayı kontrolü
                        if float(new_value).is_integer():  # Eğer ondalık kısmı 0 ise
                            new_value = int(float(new_value))
                        else:
                            new_value = float(new_value)
                except (ValueError, AttributeError):
                    pass  # Sayısal değer değilse olduğu gibi bırak

                if row_index < len(file_content) and column_name in file_content.columns:
                    file_content.loc[row_index, column_name] = new_value
                    # Sütundaki tüm değerleri kontrol et ve int'e dönüştür
                    try:
                        if all(str(x).strip().isdigit() or (isinstance(x, (int, float)) and float(x).is_integer()) 
                            for x in file_content[column_name] if pd.notna(x) and str(x).strip()):
                            file_content[column_name] = file_content[column_name].apply(
                                lambda x: int(float(x)) if pd.notna(x) and str(x).strip() else x
                            )
                    except:
                        pass
                    file_content = file_content.fillna('')
                
                log_change(user_id, file_name, "update_cell", column_name=column_name, row_index=row_index, old_value=old_value, new_value=new_value)

        # NaN değerleri kontrol et
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

def rollback_change(user_id, file_name, log_id):
    try:
        # Log kaydını al
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
            return file_content  # Hata mesajı döndür

        # İşleme göre geri alma
        if action_type == "update_cell":
            # Hücreyi eski değere döndür
            if column_name in file_content.columns and 0 <= row_index < len(file_content):
                file_content.loc[row_index, column_name] = old_value

        elif action_type == "delete_row":
            # Silinen satırı geri eklemek mümkün değil (log'da satırın tüm değerleri yok)
            return "Satır silme işlemi geri alınamaz."

        elif action_type == "add_row":
            # Eklenen satırı sil
            file_content = file_content.drop(index=row_index).reset_index(drop=True)

        elif action_type == "delete_column":
            # Silinen sütunu geri eklemek mümkün değil (log'da sütunun tüm değerleri yok)
            return "Sütun silme işlemi geri alınamaz."

        elif action_type == "add_column":
            # Eklenen sütunu sil
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







