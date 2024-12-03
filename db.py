import pyodbc
import datetime

connection = None

getdate=datetime.datetime.now()

def init_db(config):
    """Veritabanı bağlantısını başlatır."""
    global connection
    connection_str = (
        f"DRIVER={config['DRIVER']};"
        f"SERVER={config['SERVER']};"
        f"DATABASE={config['DATABASE']};"
        f"UID={config['UID']};"
        f"PWD={config['PWD']}"
    )
    connection = pyodbc.connect(connection_str)

def sign_in(email, password):
    """Kullanıcı girişini kontrol eder."""
    cur = connection.cursor()
    try:
        # Call the stored procedure Kullanici_Giris
        cur.execute("EXEC Kullanici_Giris @email=?, @password=?", (email, password))
        
        # Fetch the result
        result = cur.fetchone()
        
        # Check if login is successful (Result = 1)
        if result and result[0] != 0:
            print("Login successful")
            return result  # Return the full user data (email, password)
        else:
            print("Login failed")
            return False
    except Exception as e:
        print(f"Error in sign_in: {e}")
        return None
    finally:
        cur.close()

def sign_up(email, password):    
    cur = connection.cursor()
    try:     
        cur.execute("EXEC Kullanici_Kayit @email=?, @password=?", (email, password))
        connection.commit()
    except Exception as e:
        print(f"Error in sign_up: {e}")
    finally:
        cur.close()

def save_file(filename, filedata, user_id):
    """Dosyayı veritabanına kaydeder."""
    cur = connection.cursor()
    try:
        # Kullanıcı ID'si ile birlikte dosyayı kaydet
        cur.execute("EXEC Dosya_Kayit @filename=?, @filedata=?, @user_id=?", (filename, filedata, user_id))
        connection.commit() 
    except Exception as e:
        print(f"Error saving file: {e}")
    finally:
        cur.close()
