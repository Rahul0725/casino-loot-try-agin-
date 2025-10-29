#!/usr/bin/env python3
"""
Casino Loot & Bonus Bot for Telegram
Simple, robust. Reads offers from offers.json. Health endpoint for Render.
Set BOT_TOKEN and SUPPORT_LINK in Render environment.
"""

import os, json, logging, asyncio, threading
from pathlib import Path
from flask import Flask, jsonify
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# CONFIG (set these in Render environment variables)
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "https://t.me/trusted_Loot_Offers")
OFFERS_FILE = os.getenv("OFFERS_FILE", "offers.json")
PORT = int(os.getenv("PORT", "5000"))

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("casino-bot")

# Flask for healthcheck
flask_app = Flask(__name__)
@flask_app.route("/")
def health():
    return jsonify({"status": "ok", "service": "Casino Loot & Bonus Bot"})

def load_offers():
    p = Path(OFFERS_FILE)
    if not p.exists():
        # if missing, create a default file so bot still runs
        default = {
            "main_menu_order": [
                "🎰 Casino Offers",
                "🪙 Rummy Bonus",
                "🎯 Teen Patti Loot",
                "💵 Free Income",
                "🎁 Signup Bonus"
            ],
            "categories": {}
        }
        p.write_text(json.dumps(default, indent=2, ensure_ascii=False))
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        logger.exception("Failed to read offers.json: %s", e)
        return {"main_menu_order": [], "categories": {}}

OFFERS = load_offers()

# Telegram handlers
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🎉 Welcome to *Casino Loot & Bonus Zone!* 🇮🇳\n\n"
        "💸 Get latest casino bonuses, rummy offers & free income tricks.\n\n"
        "👇 Tap a category to view offers. Play safe!"
    )
    order = OFFERS.get("main_menu_order") or list(OFFERS.get("categories", {}).keys())
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat:{cat}")] for cat in order]
    keyboard.append([InlineKeyboardButton("📢 Join Channel / Support", url=SUPPORT_LINK)])
    keyboard.append([InlineKeyboardButton("🔄 Reload Offers (admin)", callback_data="admin:reload")])
    reply = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome, parse_mode="Markdown", reply_markup=reply)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start to open the menu. Contact support via the Join Channel button.")

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
