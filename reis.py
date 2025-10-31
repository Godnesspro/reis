from flask import Flask
import telebot
import os
import time

app = Flask(__name__)
bot = telebot.TeleBot("8258388271:AAEr5lwYGZppBtSRy-c3wXCWu4Dr_GwASfI")
CHAT_ID = 7323434112

@app.route('/')
def home():
    return "<h1>Reis Bot Aktif!</h1> <a href='/gonder'>TIKLA, FOTOĞRAFLAR GELSİN</a>"

@app.route('/gonder')
def gonder():
    try:
        bot.send_message(CHAT_ID, "Reis, iPhone'dan TÜM fotoğraflar geliyor! (Simülasyon)")
        for i in range(1, 6):
            bot.send_message(CHAT_ID, f"Foto #{i}: IMG_{i}.JPG - {time.strftime('%H:%M:%S')}")
            time.sleep(1)
        bot.send_message(CHAT_ID, "Bitti reis! Gerçek için kızı Drive'a sok.")
        return "Gönderildi!"
    except:
        return "Hata reis."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
