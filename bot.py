import requests
import statistics
import datetime
import os
import sys

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PAIR = "dgbidr"
URL = f"https://indodax.com/api/trades/{PAIR}"

print("Fetching Indodax trades...")
r = requests.get(URL, timeout=20)
print("HTTP:", r.status_code)

if r.status_code != 200:
    print("API ERROR:", r.text)
    sys.exit(1)

data = r.json()

# ambil harga close (float)
closes = [float(x["price"]) for x in data]

last = closes[0]                 # harga terakhir
ma7 = statistics.mean(closes[:7])
ma25 = statistics.mean(closes[:25])

signal = "⬆ BUY" if ma7 > ma25 else "⬇ SELL"

msg = f"""
📊 INDODAX BOT (LIVE)
Pair : {PAIR.upper()}
⏰  {datetime.datetime.utcnow()} UTC

Last : {last}
MA7  : {ma7}
MA25 : {ma25}

Signal : {signal}
"""

print(msg)

tg = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
s = requests.post(tg, json={"chat_id": CHAT_ID, "text": msg})

print("Telegram:", s.status_code)
print(s.text)
