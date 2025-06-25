import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, filters
)

# Logger setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = '8011548194:AAElZ0ka7LDTvDbTF073cWCOtjJZa91EyFQ'
OWNER_ID = 5842157752  # Replace with your Telegram user ID

# Memory stores
user_passwords = {}
saved_usernames = {}
indo_stock = {
    "5-day": {"price": 10, "stock": 0},
    "10-day": {"price": 15, "stock": 0},
    "15-day": {"price": 20, "stock": 0},
    "20-day": {"price": 25, "stock": 0},
    "25-day": {"price": 30, "stock": 0},
    "30-day": {"price": 35, "stock": 0},
}

# Random username generator
def generate_username():
    prefix = random.choice(["insta", "user", "real", "story", "snap"])
    suffix = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=random.randint(3, 6)))
    return f"{prefix}_{suffix}"

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        "👋 Welcome to Username Checker Bot!\n\n"
        "Commands:\n"
        "/random - Get 5 random usernames\n"
        "/txtfile - View copied usernames\n"
        "/passchange - Change your password\n"
        "/stock - View Indo stock (only owner)\n"
        "\nDo you want to set a password for your usernames?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Yes", callback_data="set_pass_yes"),
             InlineKeyboardButton("No", callback_data="set_pass_no")]
        ])
    )

# Handle password prompt
async def handle_pass_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if query.data == "set_pass_yes":
        context.user_data['waiting_for_password'] = True
        await query.message.reply_text("Send the password you want to set for your usernames:")
    else:
        user_passwords[user_id] = None
        await query.message.reply_text("✅ No password set.")

# Catch password input
async def handle_password_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get('waiting_for_password'):
        user_passwords[user_id] = update.message.text
        context.user_data['waiting_for_password'] = False
        await update.message.reply_text("✅ Password saved.")

# /passchange command
async def passchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['waiting_for_password'] = True
    await update.message.reply_text("📝 Send your new password:")

# /random command
async def random_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data['generated_usernames'] = []
    buttons = []
    for _ in range(5):
        uname = generate_username()
        context.user_data['generated_usernames'].append(uname)
        buttons.append([InlineKeyboardButton(uname, callback_data=f"copy_{uname}")])
    await update.message.reply_text("🧩 Choose a username to copy:", reply_markup=InlineKeyboardMarkup(buttons))

# Copy username button press
async def handle_copy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    uname = query.data.replace("copy_", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    password = user_passwords.get(user_id, "")
    if user_id not in saved_usernames:
        saved_usernames[user_id] = []
    saved_usernames[user_id].append({
        "username": uname,
        "password": password,
        "time": timestamp
    })
    await query.message.reply_text(f"📋 Copied: `{uname}`\nPassword: `{password}`\nTime: {timestamp}", parse_mode='Markdown')

# /txtfile command
async def txtfile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    records = saved_usernames.get(user_id, [])
    if not records:
        await update.message.reply_text("No copied usernames found.")
        return
    text = "📝 Copied usernames:\n\n"
    for r in records:
        text += f"{r['username']} | {r['password']} | {r['time']}\n"
    await update.message.reply_text(text)

# /stock command
async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not allowed to access this.")
        return

    buttons = []
    for label, data in indo_stock.items():
        buttons.append([
            InlineKeyboardButton(
                f"{label}: ₹{data['price']} | Stock: {data['stock']}",
                callback_data=f"edit_stock_{label}"
            )
        ])
    await update.message.reply_text("📦 Indo Selling Stock:", reply_markup=InlineKeyboardMarkup(buttons))

# Handle stock editing
async def stock_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id != OWNER_ID:
        await query.message.reply_text("❌ Only @Thefinancer2 can edit stock.")
        return
    slot = query.data.replace("edit_stock_", "")
    context.user_data['editing_stock'] = slot
    await query.message.reply_text(f"✏️ Send new stock number for {slot}:")

# Set stock from message
async def update_stock_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        return
    if 'editing_stock' in context.user_data:
        slot = context.user_data.pop('editing_stock')
        try:
            new_stock = int(update.message.text.strip())
            indo_stock[slot]["stock"] = new_stock
            await update.message.reply_text(f"✅ Stock updated: {slot} → {new_stock}")
        except ValueError:
            await update.message.reply_text("❌ Invalid number.")

# Main app
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_pass_choice, pattern="set_pass_"))
    app.add_handler(CommandHandler("passchange", passchange))
    app.add_handler(CommandHandler("random", random_usernames))
    app.add_handler(CallbackQueryHandler(handle_copy, pattern="copy_"))
    app.add_handler(CommandHandler("txtfile", txtfile))
    app.add_handler(CommandHandler("stock", stock))
    app.add_handler(CallbackQueryHandler(stock_edit, pattern="edit_stock_"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password_input))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, update_stock_amount))

    app.run_polling()
