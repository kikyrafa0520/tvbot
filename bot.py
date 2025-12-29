import requests
import os
import statistics
from datetime import datetime
from zoneinfo import ZoneInfo   # Python 3.9+

# ====== CONFIG DASAR ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PAIR = "dgbidr"        # pair di Indodax (lowercase)
RSI_PERIOD = 14

# Risk Management sederhana
TP_PERCENT = 0.04      # +4% dari harga buy_limit
SL_PERCENT = 0.02      # -2% dari harga buy_limit

INDODAX_URL = f"https://indodax.com/api/trades/{PAIR}"

# ====== WAKTU: HANYA 05:00–21:00 WIB ======
now_wib = datetime.now(ZoneInfo("Asia/Jakarta"))
hour = now_wib.hour

if not (5 <= hour <= 21):
    print(f"⏰ {now_wib} WIB — di luar jam trading (5–21). Bot berhenti.")
    raise SystemExit(0)

print(f"⏰ {now_wib} WIB — bot berjalan...")

# ====== FETCH TRADES DARI INDODAX ======
print("Fetching Indodax trades...")
r = requests.get(INDODAX_URL, timeout=20)
print("HTTP:", r.status_code)

if r.status_code != 200:
    print("API ERROR:", r.text)
    raise SystemExit(1)

trades = r.json()

# Harga (trades terbaru ada di index 0)
closes = [float(t["price"]) for t in trades]

if len(closes) < 60:
    print("Data trades kurang untuk analisa (butuh > 60).")
    raise SystemExit(0)

last = closes[0]                 # harga terakhir
ma7  = statistics.mean(closes[:7])
ma25 = statistics.mean(closes[:25])
ma50 = statistics.mean(closes[:50])

# ====== FUNGSI RSI ======
def rsi(values, period=14):
    """RSI sederhana dari deret harga terbaru (values[0] = harga terbaru)."""
    gains = []
    losses = []

    for i in range(1, period + 1):
        change = values[i-1] - values[i]
        if change > 0:
            gains.append(change)
        else:
            losses.append(abs(change))

    avg_gain = sum(gains) / period if gains else 0.000001
    avg_loss = sum(losses) / period if losses else 0.000001

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

RSI = rsi(closes, RSI_PERIOD)

# ====== RULE TREND & SIGNAL ======
trend = "UP" if ma25 > ma50 else "DOWN"

signal = "NO_TRADE"
mode   = "NONE"

buy_limit_price = None
tp_price = None
sl_price = None

# Kondisi BUY (trend naik + koreksi sehat)
if (ma7 > ma25 > ma50) and RSI < 40:
    signal = "BUY_LIMIT"
    mode = "WAIT_FOR_DROP"
    # BUY LIMIT kita pakai sedikit di bawah MA25 (diskon ~1%)
    buy_limit_price = round(ma25 * 0.99)       # dibulatkan ke IDR
    tp_price        = round(buy_limit_price * (1 + TP_PERCENT))
    sl_price        = round(buy_limit_price * (1 - SL_PERCENT))

# Kondisi SELL (optional, masih kita tampilkan infonya saja)
elif (ma7 < ma25 < ma50) and RSI > 60:
    signal = "SELL"
    mode = "TREND_DOWN"
else:
    signal = "NO_TRADE"
    mode = "NEUTRAL"

# ====== SUSUN PESAN TELEGRAM ======
lines = []
lines.append("📊 INDODAX BOT (LIVE)")
lines.append("")
lines.append(f"Pair : DGB/IDR")
lines.append(f"Waktu: {now_wib} WIB")
lines.append("")
lines.append(f"Last  : {last}")
lines.append(f"MA7   : {round(ma7, 2)}")
lines.append(f"MA25  : {round(ma25, 2)}")
lines.append(f"MA50  : {round(ma50, 2)}")
lines.append("")
lines.append(f"RSI14 : {round(RSI, 2)}")
lines.append(f"Trend : {'⬆ UP' if trend == 'UP' else '⬇ DOWN'}")
lines.append("")

if signal == "BUY_LIMIT":
    lines.append("Signal : ✅ BUY LIMIT (TRADING PLAN)")
    lines.append("")
    lines.append("📌 Rencana BUY (bukan eksekusi sekarang):")
    lines.append(f"   • Harga saat ini : {last}")
    lines.append(f"   • Area BUY      : {buy_limit_price} IDR (sekitar MA25 - 1%)")
    lines.append("")
    lines.append("🎯 Target:")
    lines.append(f"   • TP (±+{int(TP_PERCENT*100)}%) : {tp_price} IDR")
    lines.append(f"   • SL (−{int(SL_PERCENT*100)}%) : {sl_price} IDR")
    lines.append("")
    lines.append("Catatan:")
    lines.append("   • Tunggu harga TURUN ke area BUY sebelum entry.")
    lines.append("   • Ini hanya rencana, eksekusi tetap manual / sesuai strategi Anda.")
elif signal == "SELL":
    lines.append("Signal : ❌ SELL BIAS (TREND TURUN)")
    lines.append("")
    lines.append("Catatan:")
    lines.append("   • Trend utama turun, hati-hati membuka posisi BUY baru.")
    lines.append("   • Bisa dipakai sebagai warning untuk kurangi posisi.")
else:
    lines.append("Signal : ⚠ NO TRADE (SIDEWAYS / TIDAK JELAS)")
    lines.append("")
    lines.append("Catatan:")
    lines.append("   • Kondisi belum ideal untuk BUY LIMIT.")
    lines.append("   • Tunggu momentum yang lebih jelas (trend + RSI).")

msg = "\n".join(lines)

print("\n===== PREVIEW PESAN =====")
print(msg)

# ====== KIRIM KE TELEGRAM ======
if not BOT_TOKEN or not CHAT_ID:
    print("❗ BOT_TOKEN / CHAT_ID belum di-set di Secrets.")
    raise SystemExit(1)

tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": msg
}

tr = requests.post(tg_url, json=payload)
print("\nTelegram:", tr.status_code)
print(tr.text)
