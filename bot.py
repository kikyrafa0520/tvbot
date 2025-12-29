import requests
import time
import datetime
import statistics
import os
import sys

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOL = "DGBIDR"
RES = "60"

now = int(time.time())
frm = now - (50 * 60 * 60)

URL = "https://indodax.com/tradingview/history"

params = {
    "symbol": SYMBOL,
    "resolution": RES,
    "from": frm,
    "to": now
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

print("Fetching TradingView...")
r = requests.get(URL, params=params, headers=headers, timeout=30)
print("HTTP:", r.status_code)

print("Raw response text:", r.text[:400])

try:
    data = r.json()
except Exception as e:
    print("JSON parse error:", e)
    sys.exit(1)

print("Status:", data.get("s"))

if data.get("s") != "ok":
    print("API returned error:", data)
    sys.exit(1)

closes = data["c"]

last = closes[-1]
ma7 = statistics.mean(closes[-7:])
ma25 = statistics.mean(closes[-25:])

signal = "⬆ BUY" if ma7 > ma25 else "⬇ SELL"

msg = f"""
📊 TRADINGVIEW BOT (1H)
Exchange : INDODAX
Pair     : {SYMBOL}
⏰ {datetime.datetime.utcnow()} UTC

Last : {last}
MA7  : {ma7}
MA25 : {ma25}

Signal : {signal}
"""

tg = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
s = requests.post(tg, json={"chat_id": CHAT_ID, "text": msg})

print("Telegram:", s.status_code)
print(s.text)
