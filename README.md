# NewMusicerabot

Starter Telegram bot with:
- /start and /help
- owner-only broadcast to groups where the bot is a member
- text/link broadcasting
- forwarded/replied messages can be broadcast with `/broadcast` as a reply
- basic group tracking in SQLite

## Setup
1. Install Python 3.10+.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`.
4. Put your BotFather token in `BOT_TOKEN`.
5. Keep `OWNER_ID=8871204897`.
6. Run:
   `python bot.py`

The bot must be added to groups before it can send messages there. Telegram permissions and privacy settings can affect what the bot can see/send.

## Broadcast
- `/broadcast Hello everyone`
- Reply to any Telegram message with `/broadcast` to copy that message to tracked groups.

Use broadcasting responsibly and only to groups where you have permission. This starter does not include music downloading/voice-chat playback yet; that is the next module.
