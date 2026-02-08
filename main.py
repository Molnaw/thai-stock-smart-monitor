import yfinance as yf
import requests
from datetime import datetime, timedelta

# --- ตั้งค่าพื้นฐาน ---
TOKEN = 'YOUR_LINE_OR_TELEGRAM_TOKEN' # ใส่ Token ของคุณตรงนี้
stocks = ['ADVANC.BK', 'TISCO.BK', 'BDMS.BK', 'PTT.BK']

def send_message(msg):
    print(f"Sending: {msg}")
    # ใส่โค้ดส่ง Line/Telegram ของคุณที่นี่

def check_stock_and_dividends():
    for symbol in stocks:
        stock = yf.Ticker(symbol)
        
        # 1. ดึงข้อมูลราคาปัจจุบัน (ของเดิม)
        data = stock.history(period='2d')
        if len(data) < 2: continue
        
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-0]
        change_pct = ((current_price - prev_price) / prev_price) * 100
        
        # 2. ดึงข้อมูลปันผล (เพิ่มใหม่!)
        info = stock.info
        ex_date_timestamp = info.get('exDividendDate')
        div_rate = info.get('dividendRate', 0)
        
        # ตรวจสอบแจ้งเตือนด่วน (ราคาเปลี่ยน > 3%)
        if abs(change_pct) >= 3.0:
            emoji = '🔥' if change_pct > 0 else '🚨'
            send_message(f"⚠️ แจ้งเตือนด่วน: {symbol}\nราคา: {current_price:.2f} ({change_pct:+.2f}%){emoji}")

        # ตรวจสอบแจ้งเตือน XD (เตือนล่วงหน้า 7 วัน)
        if ex_date_timestamp:
            ex_date = datetime.fromtimestamp(ex_date_timestamp)
            days_to_xd = (ex_date - datetime.now()).days
            
            if 0 <= days_to_xd <= 7:
                send_message(f"📢 แจ้งเตือนปันผล! {symbol}\n📅 วันขึ้น XD: {ex_date.strftime('%d/%m/%Y')}\n💰 ปันผล: {div_rate} บาท/หุ้น\n⏳ อีก {days_to_xd} วันสุดท้าย!")

# --- ส่วนของการตั้งเวลารัน ---
now = datetime.utcnow() + timedelta(hours=7) # เวลาไทย
if now.hour == 10 or now.hour == 17:
    check_stock_and_dividends()
