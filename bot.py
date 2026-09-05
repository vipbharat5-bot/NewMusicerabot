import os
import sqlite3
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "8871204897"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Put it in .env")

DB = "bot.db"

def db():
    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            chat_id INTEGER PRIMARY KEY,
            title TEXT,
            active INTEGER DEFAULT 1
        )
    """)
    con.commit()
    return con

def save_group(chat_id, title):
    con = db()
    con.execute(
        "INSERT OR REPLACE INTO groups(chat_id,title,active) VALUES(?,?,1)",
        (chat_id, title or str(chat_id))
    )
    con.commit()
    con.close()

def get_groups():
    con = db()
    rows = con.execute("SELECT chat_id,title FROM groups WHERE active=1").fetchall()
    con.close()
    return rows

def deactivate_group(chat_id):
    con = db()
    con.execute("UPDATE groups SET active=0 WHERE chat_id=?", (chat_id,))
    con.commit()
    con.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        save_group(update.effective_chat.id, update.effective_chat.title)

    await update.message.reply_text(
        "🎵 NewMusicerabot is online!\n\n"
        "Commands:\n"
        "/play <song> — music module coming next\n"
        "/help — help\n"
        "/broadcast <text> — owner only\n\n"
        "Reply to a message with /broadcast to broadcast that message."
    )

async def track_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat and chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        save_group(chat.id, chat.title)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 NewMusicerabot Help\n\n"
        "/start — start bot\n"
        "/help — this help\n"
        "/broadcast <text> — owner-only group broadcast\n"
        "Reply to a message with /broadcast to copy it to groups."
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Owner only.")
        return

    source = update.message
    text = " ".join(context.args).strip()

    if not text and not source.reply_to_message:
        await source.reply_text(
            "Usage:\n/broadcast Your message\n\n"
            "Or reply to a message and send /broadcast"
        )
        return

    groups = get_groups()
    if not groups:
        await source.reply_text("⚠️ No tracked groups yet. Add the bot to groups and use /start there.")
        return

    sent = 0
    failed = 0

    for chat_id, title in groups:
        try:
            if source.reply_to_message:
                await source.reply_to_message.copy(chat_id=chat_id)
            else:
                await context.bot.send_message(chat_id=chat_id, text=text)
            sent += 1
            await asyncio.sleep(0.15)
        except Exception:
            failed += 1
            # Keep the group tracked: temporary errors should not permanently disable it.

    await source.reply_text(
        f"📢 Broadcast finished.\n\n✅ Sent: {sent}\n⚠️ Failed: {failed}"
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args).strip()
    if not query:
        await update.message.reply_text("Use: /play <song name>")
        return
    await update.message.reply_text(
        f"🔎 Music request received: {query}\n\n"
        "Voice-chat playback module will be added in the next step."
    )

def main():
    db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("play", play))

    # Track group activity so groups are known to the bot.
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & ~filters.COMMAND,
        track_group
    ))

    print("NewMusicerabot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
