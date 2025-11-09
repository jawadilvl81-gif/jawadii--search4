# main.py - TeraBox Rocket Downloader Bot
import telebot
import requests
import threading
import time
from flask import Flask
import os

# === CONFIG ===
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# === PREMIUM USERS (Manually add after JazzCash payment) ===
PREMIUM_USERS = [123456789]  # ← Yahan user IDs daalo

# === DAILY LIMIT TRACKER (Simple dict - resets on restart) ===
FREE_LIMIT = {}  # {user_id: count}

# === KEEP ALIVE ===
def keep_alive():
    while True:
        time.sleep(60)
        print("Bot is alive...")

threading.Thread(target=keep_alive, daemon=True).start()

# === COMMANDS ===
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id,
        "🚀 *TeraBox Rocket Downloader*\n\n"
        "TeraBox link bhejo → file yahin!\n"
        "🔥 Free: 1 file/day\n"
        "💎 Premium: Unlimited → /premium\n\n"
        "Made with ❤️ for Pakistan",
        parse_mode='Markdown')

@bot.message_handler(commands=['premium'])
def premium(m):
    bot.send_message(m.chat.id,
        "💎 *Premium Pack*\n"
        "→ Unlimited Downloads\n"
        "→ No Ads\n"
        "→ Fast Speed\n\n"
        "💰 *₹300/month*\n"
        "📲 JazzCash: 03XX-XXXXXXX\n"
        "Payment proof bhejo → @YourAdmin",
        parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_cmd(m):
    bot.send_message(m.chat.id,
        "📋 *Commands*\n"
        "/start - Start\n"
        "/premium - Upgrade\n"
        "/stats - Status",
        parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def stats(m):
    bot.send_message(m.chat.id, "📊 Bot is *LIVE* & 24/7 Active! 🚀", parse_mode='Markdown')

# === MAIN DOWNLOADER ===
@bot.message_handler(func=lambda m: "terabox.com" in m.text or "1024tera.com" in m.text)
def download_terabox(m):
    user_id = m.from_user.id
    link = m.text.strip()

    # === FREE USER LIMIT ===
    if user_id not in PREMIUM_USERS:
        today = time.strftime("%Y-%m-%d")
        key = f"{user_id}_{today}"
        FREE_LIMIT[key] = FREE_LIMIT.get(key, 0)
        if FREE_LIMIT[key] >= 1:
            bot.send_message(m.chat.id, "⚠️ *Free Limit*: 1 file/day.\n"
                                        "Upgrade → /premium", parse_mode='Markdown')
            return
        FREE_LIMIT[key] += 1

    bot.send_message(m.chat.id, "🔍 Link scan kar raha hoon...")

    try:
        api_url = f"https://terabox-dl.herokuapp.com/?url={link}"
        res = requests.get(api_url, timeout=30).json()

        if res.get('error'):
            bot.send_message(m.chat.id, "❌ Link expired ya invalid!")
            return

        direct_link = res.get('direct_link')
        file_name = res.get('filename', 'TeraBox_File')

        if not direct_link:
            bot.send_message(m.chat.id, "❌ Direct link nahi mila!")
            return

        bot.send_message(m.chat.id, f"⬇️ Downloading: *{file_name}*...", parse_mode='Markdown')

        bot.send_document(
            m.chat.id,
            direct_link,
            caption=f"✅ @TeraBoxRocket\n"
                    f"💎 Premium? /premium",
            timeout=600
        )

    except Exception as e:
        bot.send_message(m.chat.id, "⚠️ Error: API down ya link issue.\n"
                                    "Try again later!")

# === FLASK WEB ===
@app.route('/')
def home():
    return "TeraBox Rocket Bot is LIVE! 🚀"

# === RUN ===
def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=8080)
