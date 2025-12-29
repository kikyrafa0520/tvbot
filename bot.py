import requests
import os
import statistics
from datetime import datetime
from zoneinfo import ZoneInfo   # Python 3.9+
import math

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PAIR = "dgbidr"        # pair Indodax (huruf kecil)
RSI_PERIOD = 14

INDODAX_URL = f"https://indodax.com/api/trades/{PAIR}"

# =========================
#   Waktu Indonesia (WIB)
# =========================
now_wib = datetime.now(ZoneInfo("Asia/Jakarta"))
hour = now_wib.hour

# hanya jalan 05:00–21:00 WIB
if not (5 <= hour <= 21):
    print(f"⏰ Sekarang {now_wib} WIB — di luar jam trading. Bot berhenti.")
    exit(0)

print(f"⏰ Sekarang {now_wib} WIB — bot berjalan...")

# =========================
#   Fetch trades
# =========================
print("Fetching Indodax trades...")
r = requests.get(INDODAX_URL)
print("HTTP:", r.status_code)

if r.status_code != 200:
    print("Gagal ambil data")
    exit(1)

trades = r.json()

# ambil hanya harga terakhir (closes)
closes = [float(t["price"]) for t in trades]

if len(closes) < 60:
    print("Data kurang untuk analisa")
    exit(1)

last = closes[0:1][0]

ma7  = statistics.mean(closes[:7])
ma25 = statistics.mean(closes[:25])
ma50 = statistics.mean(closes[:50])

# =========================
#   RSI Function
# =========================
def rsi(values, period=14):
    gains = []
    losses = []

    for i in range(1, period + 1):
        change = values[i-1] - values[i]
        if change > 0:
            gains.append(change)
        else:
            losses.append(abs(change))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period if sum(losses) != 0 else 0.000001

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

RSI = rsi(closes, RSI_PERIOD)

# =========================
#   Trend + Signal Rules
# =========================
trend = "UP" if ma25 > ma50 else "DOWN"

signal = "NO TRADE"

if ma7 > ma25 and ma25 > ma50 and RSI < 30:
    signal = "BUY"
elif ma7 < ma25 and ma25 < ma50 and RSI > 70:
    signal = "SELL"

# =========================
#   Build Message
# =========================
msg = f"""
📊 INDODAX BOT (LIVE)

Pair : DGB/IDR
⏰  {now_wib}

Last : {last}
MA7  : {ma7}
MA25 : {ma25}
MA50 : {ma50}

RSI14 : {round(RSI,2)}
Trend : {"⬆ UP" if trend=="UP" else "⬇ DOWN"}

Signal : {("✅ BUY" if signal=="BUY" else "❌ SELL" if signal=="SELL" else "⚠ NO TRADE")}
"""

print(msg)

# =========================
#   Kirim Telegram
# =========================
if BOT_TOKEN and CHAT_ID:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    tr = requests.post(url, json=payload)

    print("\nTelegram:", tr.status_code)
    print(tr.text)
else:
    print("❗ BOT_TOKEN / CHAT_ID belum di-set")
