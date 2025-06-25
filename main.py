from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = '8011548194:AAElZ0ka7LDTvDbTF073cWCOtjJZa91EyFQ'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send usernames line‑by‑line. I'll check duplicates!")

async def check_duplicates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usernames = update.message.text.strip().splitlines()
    seen, duplicates = set(), set()
    for u in usernames:
        c = u.strip().lower()
        if c in seen:
            duplicates.add(c)
        else:
            seen.add(c)
    if duplicates:
        await update.message.reply_text("❌ Duplicates:\n" + "\n".join(sorted(duplicates)))
    else:
        await update.message.reply_text("✅ All unique!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_duplicates))
    app.run_polling()
