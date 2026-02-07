import yfinance as yf
import requests
import os
from datetime import datetime

# หุ้น 4 กลุ่มที่เราเฝ้าดู
STOCKS = {
    'ADVANC.BK': 'ICT (AIS)',
    'TISCO.BK': 'Banking',
    'BDMS.BK': 'Healthcare',
    'PTT.BK': 'Energy'
}

# ความฉลาด: เตือนด่วนเฉพาะเมื่อราคาเหวี่ยงเกิน 3% เท่านั้น
ALERT_THRESHOLD = 3.0 

def send_telegram(message):
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=15)
    except:
        print("Network error")

def monitor():
    # เวลาไทย (UTC+7)
    now_hour = (datetime.utcnow().hour + 7) % 24
    summary = []
    urgent_alerts = []

    for symbol, group in STOCKS.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period='2d')
            if len(df) < 2: continue

            current = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2]
            diff = ((current - prev) / prev) * 100

            summary.append(f"• {symbol}: {current:.2f} ({diff:+.2f}%)")

            # แจ้งเตือนด่วนถ้าขยับแรงเกิน 3%
            if abs(diff) >= ALERT_THRESHOLD:
                icon = "🔥" if diff > 0 else "🚨"
                urgent_alerts.append(f"{icon} <b>{symbol} ขยับแรง!</b>\nราคา: {current:.2f} ({diff:+.2f}%)")
        except:
            continue

    # ส่งสรุปเช้า (10:00) และ เย็น (17:00) ตามเวลาไทย
    if now_hour == 10 or now_hour == 17:
        header = "<b>🔔 เปิดตลาดเช้า</b>\n" if now_hour == 10 else "<b>📝 สรุปตลาดปิด</b>\n"
        send_telegram(header + "\n".join(summary))

    # ถ้ามีเหตุการณ์ด่วน ส่งทันที
    if urgent_alerts:
        send_telegram("⚠️ <b>แจ้งเตือนด่วน:</b>\n" + "\n".join(urgent_alerts))

if __name__ == "__main__":
    monitor()
