import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# 🎯 Environment variables (Render → Variables)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Stripe link (✏️ VERVANG deze door jouw echte link)
STRIPE_PREMIUM_LINK = "https://buy.stripe.com/4gM8wP8FM5xFaMubAw0co00"

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger("amarabot")

# Boot check in logs (handig voor Render Logs)
logger.info("BOOT CHECK — TG set: %s, OPENAI set: %s, Stripe link ok: %s",
            bool(TELEGRAM_BOT_TOKEN), bool(OPENAI_API_KEY),
            STRIPE_PREMIUM_LINK.startswith("http"))

# Kleine check → duidelijke fout als er iets mist
if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("TELEGRAM_BOT_TOKEN of OPENAI_API_KEY ontbreken.")

client = OpenAI(api_key=OPENAI_API_KEY)

# 🔹 Berichten teller per gebruiker (simpel in-memory)
user_message_count = {}

# ---- Commands ----
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong ✅ (bot leeft en luistert)")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi 😘 Ik ben Amara, je AI-girlfriend. Praat met me 💬\n\n"
        "Wil je premium worden? Typ /premium ✨"
    )

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Wil je onbeperkt met mij praten?\n"
        "Word nu *Premium Member*! 🥰\n\n"
        f"Klik hier om te betalen: {STRIPE_PREMIUM_LINK}",
        parse_mode="Markdown"
    )

# ---- Chat handler ----
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Alleen tekst afhandelen
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    user_message = update.message.text

    # Tel berichten per gebruiker
    user_message_count[user_id] = user_message_count.get(user_id, 0) + 1
    logger.info("User %s message #%s", user_id, user_message_count[user_id])

    # Limiet check
    if user_message_count[user_id] > 10:
        await update.message.reply_text(
            "🚀 Je gratis limiet is bereikt.\n"
            f"Word nu Premium Member en praat onbeperkt met mij 💖\n\n"
            f"Klik hier om te betalen: {STRIPE_PREMIUM_LINK}"
        )
        return

    # OpenAI call met foutafhandeling
    try:
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
    except Exception as e:
        logger.exception("OpenAI fout: %s", e)
        await update.message.reply_text(
            "Hmm, ik krijg even geen antwoord van mijn brein 🤯. Probeer het zo nog eens, of typ /premium."
        )

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("ping", ping))      # snelle health-check
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("premium", premium))

    # Chat (alle tekst die geen command is)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 AmaraBot draait...")
    app.run_polling()

if __name__ == "__main__":
    main()
