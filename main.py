import os
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import pytz
import random
import json
from keep_alive import keep_alive

# Load motivational messages
with open("motivation.json", "r") as f:
    motivation_data = json.load(f)

# Timezone
tz = pytz.timezone("Africa/Lagos")

# API credentials
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
session_string = os.environ['SESSION_STRING']

client = TelegramClient(StringSession(session_string), api_id, api_hash)

# Channels
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

# Filters
BLOCKED_WORDS = ['investment', 'bitcoin', 'btc']
REQUIRED_WORDS = ['tp', 'sl', 'take profit', 'stop loss']
daily_counter = 0
last_reset = datetime.now(tz).date()
morning_sent = False
motivational_index = 0
sent_messages = set()

def reset_daily():
    global daily_counter, morning_sent, last_reset, motivational_index
    today = datetime.now(tz).date()
    if today != last_reset:
        daily_counter = 0
        morning_sent = False
        motivational_index = (motivational_index + 1) % len(motivation_data)
        last_reset = today

def is_valid_signal(msg: str) -> bool:
    lower = msg.lower()
    if any(block in lower for block in BLOCKED_WORDS):
        return False
    return any(req in lower for req in REQUIRED_WORDS)

async def send_morning_motivation():
    global morning_sent
    if morning_sent:
        return
    data = motivation_data[motivational_index]
    img_path = f"images/{data['id']}.jpg"
    await client.send_file(TARGET_CHANNEL, img_path, caption=f"🌞 Good Morning Traders!\n\n_{data['text']}_\n\nGet ready, first signal drops shortly.")
    morning_sent = True

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def signal_handler(event):
    global daily_counter
    reset_daily()

    msg = event.message.message
    if event.id in sent_messages or daily_counter >= 6:
        return
    if not is_valid_signal(msg):
        return

    if not morning_sent:
        await send_morning_motivation()

    captioned = f"{msg}\n\n_By @RealDonwise 🔥 | Donwise Copytrade Vault_"
    await client.send_message(TARGET_CHANNEL, captioned, parse_mode='markdown')
    sent_messages.add(event.id)
    daily_counter += 1

async def main():
    await client.start()
    print("Bot is running...")
    await client.run_until_disconnected()

keep_alive()
asyncio.get_event_loop().run_until_complete(main())
