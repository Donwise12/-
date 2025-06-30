import os
import asyncio
import logging
import json
from datetime import datetime, timedelta, date
import pytz
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from keep_alive import keep_alive

# Enable logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
session_str = os.environ['SESSION_STRING']

# Initialize Telegram client
client = TelegramClient(StringSession(session_str), api_id, api_hash)

# Timezone
tz = pytz.timezone("Africa/Lagos")

# Source and target channels
SOURCE_CHANNELS = [
    'https://t.me/GaryGoldLegacy',
    'https://t.me/firepipsignals',
    'https://t.me/habbyforex',
    'https://t.me/Goldforexsignalfx11',
    'https://t.me/Forex_Top_Premium_Signals',
    'https://t.me/forexgdp0',
    'https://t.me/bengoldtrader',
    'https://t.me/kojoforextrades'
]
TARGET_CHANNEL = 'https://t.me/DonwiseVault'

# Signal tracking
daily_signals = set()
last_reset_date = None
morning_sent = False

# --- DAILY RESET ---
def reset_daily_state():
    global daily_signals, last_reset_date, morning_sent
    today = datetime.now(tz).date()
    if last_reset_date != today:
        logging.info("🔁 New day: Resetting signal count and morning post status.")
        daily_signals = set()
        morning_sent = False
        last_reset_date = today

# --- MOTIVATIONAL POST ---
def get_daily_motivation():
    with open("motivational/motivation.json", "r") as f:
        data = json.load(f)
    day = (date.today().day % 28) or 28
    return next((item for item in data if item["id"] == day), None)

async def send_morning_message():
    global morning_sent
    if not morning_sent:
        motivation = get_daily_motivation()
        if motivation:
            file_path = f"motivational/{motivation['image']}"
            caption = (
                f"🌞 Good Morning Donwise Vault!\n\n"
                f"_{motivation['text']}_\n\n"
                f"Are you ready for today's signals? Let's go! 💥"
            )
            await client.send_file(TARGET_CHANNEL, file=file_path, caption=caption, parse_mode='markdown')
            logging.info("✅ Sent motivational post.")
        morning_sent = True

# --- SIGNAL VALIDATION ---
def is_valid_signal(msg: str) -> bool:
    msg_l = msg.lower()
    if 'sl' in msg_l and 'tp' in msg_l:
        return True
    return False

# --- FORWARD SIGNAL ---
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    global daily_signals
    reset_daily_state()

    if len(daily_signals) >= 6:
        return

    if event.media:
        return

    msg = event.message.message.strip()
    if not is_valid_signal(msg):
        return

    # Prevent duplicates
    if msg in daily_signals:
        logging.info("⚠️ Duplicate signal skipped.")
        return

    # Send motivational post if not already
    if not morning_sent:
        await send_morning_message()

    # Tag and send signal
    final_msg = f"{msg}\n\n_By @RealDonwise 🔥 | Donwise Copytrade Vault_"
    await client.send_message(TARGET_CHANNEL, final_msg, parse_mode='markdown')
    daily_signals.add(msg)
    logging.info(f"📩 Forwarded signal: {msg[:40]}...")

# --- RUN ---
async def main():
    await client.start()
    logging.info("🚀 Bot started.")
    await client.run_until_disconnected()

keep_alive()
client.loop.run_until_complete(main())
