import mysql.connector
import sys

try:
    db = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="botgifts"
    )

    if db.is_connected():
        print("Berhasil terhubung ke database")
        cursor = db.cursor(dictionary=True)
        
    else:
        print("Gagal terhubung ke database")
        sys.exit()

except mysql.connector.Error as err:
    print(f"Terjadi kesalahan: {err}")
    sys.exit()
