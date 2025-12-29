import requests
import statistics
import datetime
import os
import sys

# ===== Ambil TOKEN & CHAT_ID dari Secrets =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ===== DEBUG — CEK apakah CHAT_ID terbaca =====
print("CHAT_ID loaded =", CHAT_ID)

PAIR = "dgbidr"
URL = f"https://indodax.com/api/trades/{PAIR}"

print("Fetching Indodax trades...")
r = requests.get(URL, timeout=20)
print("HTTP:", r.status_code)

if r.status_code != 200:
    print("API ERROR:", r.text)
    sys.exit(1)

data = r.json()

# ===== Ambil harga closing terakhir =====
closes = [float(x["price"]) for x in data]

last = closes[0]
ma7 = statistics.mean(closes[:7])
ma25 = statistics.mean(closes[:25])

signal = "⬆ BUY" if ma7 > ma25 else "⬇ SELL"

# ==== Waktu UTC yang benar ====
now_utc = datetime.datetime.now(datetime.UTC)

msg = f"""
📊 INDODAX BOT (LIVE)
Pair : {PAIR.upper()}
⏰  {now_utc}

Last : {last}
MA7  : {ma7}
MA25 : {ma25}

Signal : {signal}
"""

print(msg)

# ===== Kirim ke Telegram =====
tg = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
s = requests.post(tg, json={"chat_id": CHAT_ID, "text": msg})

print("Telegram:", s.status_code)
print(s.text)
