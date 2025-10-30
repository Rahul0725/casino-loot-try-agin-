from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "6343381167:AAErcoKwRG3rB7QpxdmtS0F9JbrV9PYN9mg"
CHANNEL_LINK = "https://t.me/trusted_Loot_Offers"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎰 Casino Offers", callback_data="casino")],
        [InlineKeyboardButton("🪙 Rummy Bonus", callback_data="rummy")],
        [InlineKeyboardButton("🎯 Teen Patti Loot", callback_data="teenpatti")],
        [InlineKeyboardButton("💵 Free Income", callback_data="income")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎁 Choose a category:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category_links = {
        "casino": "🎰 Casino Offers:\n1. All lottery site\n2. Yono Game\n3. MostBet",
        "rummy": "🪙 Rummy Bonus:\n1. Yono Rummy\n2. Ok Rummy",
        "teenpatti": "🎯 Teen Patti Loot:\n1. BDG Slot",
        "income": "💵 Free Income:\n1. Task Earning\n2. 500 Spin Tricks"
    }

    if query.data in category_links:
        await query.edit_message_text(
            text=f"{category_links[query.data]}\n\n👉 Visit Offers: {CHANNEL_LINK}"
        )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", start))
app.add_handler(CommandHandler("menu", start))
app.add_handler(CommandHandler("offers", start))
app.add_handler(CommandHandler("casino", start))
app.add_handler(CommandHandler("rummy", start))
app.add_handler(CommandHandler("teenpatti", start))
app.add_handler(CommandHandler("income", start))

from telegram.ext import CallbackQueryHandler
app.add_handler(CallbackQueryHandler(button_handler))

print("✅ Bot started...")
app.run_polling()
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    if data.startswith("cat:"):
        cat = data.split(":",1)[1]
        await show_category(cat, query, context)
        return
    if data == "back:menu":
        order = OFFERS.get("main_menu_order") or list(OFFERS.get("categories", {}).keys())
        keyboard = [[InlineKeyboardButton(c, callback_data=f"cat:{c}")] for c in order]
        keyboard.append([InlineKeyboardButton("📢 Join Channel / Support", url=SUPPORT_LINK)])
        keyboard.append([InlineKeyboardButton("🔄 Reload Offers (admin)", callback_data="admin:reload")])
        await query.edit_message_text("🎰 Main Menu — choose a category:", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    if data.startswith("admin:"):
        sub = data.split(":",1)[1]
        if sub == "reload":
            global OFFERS
            OFFERS = load_offers()
            await query.edit_message_text("✅ Offers reloaded from offers.json. Use /start to open menu.")
        return

async def show_category(category_name: str, query, context):
    cats = OFFERS.get("categories", {})
    offers = cats.get(category_name, [])
    if not offers:
        keyboard = [
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back:menu")],
            [InlineKeyboardButton("📢 Join Channel / Support", url=SUPPORT_LINK)]
        ]
        await query.edit_message_text(f"No offers found for *{category_name}*.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    keyboard = []
    for o in offers:
        name = o.get("name", "Offer")
        url = o.get("url", "")
        if url:
            keyboard.append([InlineKeyboardButton(name, url=url)])
        else:
            keyboard.append([InlineKeyboardButton(name, callback_data=f"note:{name}")])
    keyboard.append([InlineKeyboardButton("⬅️ Back to Menu", callback_data="back:menu")])
    keyboard.append([InlineKeyboardButton("📢 Join Channel / Support", url=SUPPORT_LINK)])
    await query.edit_message_text(f"🔹 *{category_name}* — choose an offer:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# Run Flask + Telegram
def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

async def run_bot_async():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set. Please set it in Render environment variables.")
        return
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))
    await app.run_polling(stop_signals=None)

def start_all():
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_bot_async())
    except Exception as e:
        logger.exception("Bot stopped: %s", e)

if __name__ == "__main__":
    logger.info("Starting Casino Loot & Bonus Bot...")
    start_all()
