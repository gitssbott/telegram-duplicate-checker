import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send usernames line‑by‑line. I’ll check for duplicates.")

# Username check
async def check_duplicates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usernames = update.message.text.strip().splitlines()
    seen = set()
    duplicates = set()
    for name in usernames:
        n = name.strip().lower()
        if n in seen:
            duplicates.add(n)
        seen.add(n)

    if duplicates:
        await update.message.reply_text("❌ Duplicates found:\n" + "\n".join(sorted(duplicates)))
    else:
        await update.message.reply_text("✅ All usernames are unique!")

# App start
if __name__ == "__main__":
    application = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_duplicates))

    application.run_polling()
