import requests
import time
import datetime
import statistics
import os
import sys

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOL = "INDODAX:DGBIDR"   # ambil data harga TradingView INDODAX
RES = "60"                  # 1 jam

now = int(time.time())
frm = now - (50 * 60 * 60)   # 50 jam ke belakang

URL = "https://indodax.com/tradingview/history"

params = {
    "symbol": SYMBOL,
    "resolution": RES,
    "from": frm,
    "to": now
}

print("Fetching TradingView...")
r = requests.get(URL, params=params)
print("HTTP:", r.status_code)

if r.status_code != 200:
    print("API ERROR:", r.text)
    sys.exit(1)

data = r.json()

print("TradingView status:", data.get("s"))

if data.get("s") != "ok":
    print("TradingView error:", data)
    sys.exit(1)

closes = data["c"]

last = closes[-1]
ma7 = statistics.mean(closes[-7:])
ma25 = statistics.mean(closes[-25:])

signal = "⬆ BUY" if ma7 > ma25 else "⬇ SELL"

msg = f"""
📊 TRADINGVIEW BOT (1H)
Pair : {SYMBOL}
⏰  {datetime.datetime.utcnow()} UTC

Last : {last:.6f}
MA7  : {ma7:.6f}
MA25 : {ma25:.6f}

Signal : {signal}
"""

print(msg)

tg = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
s = requests.post(tg, json={
    "chat_id": CHAT_ID,
    "text": msg
})

print("Telegram:", s.status_code)
print(s.text)
