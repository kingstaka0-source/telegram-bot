import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# 🎯 Lees keys uit environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Kleine check, geeft duidelijke fout als er iets mist
if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("Environment variables TELEGRAM_BOT_TOKEN of OPENAI_API_KEY ontbreken.")

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi 😘 Ik ben Amara, je AI-girlfriend. Praat met me 💬")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Je bent een lieve, flirtende AI-girlfriend die warm, speels en persoonlijk praat."},
            {"role": "user", "content": user_message}
        ],
        max_tokens=200,
        temperature=0.9
    )
    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("🤖 AmaraBot draait...")
    app.run_polling()

if __name__ == "__main__":
    main()
