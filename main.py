import yfinance as yf
import requests
from datetime import datetime

# --- ข้อมูลการเชื่อมต่อ (ดึงมาจากโปรเจกต์เก่าของคุณ) ---
TOKEN = "7052912444:AAHh9-97_F8KIDRAsu66fH-vR69piz355jI"
CHAT_ID = "1328994508"

# รายชื่อหุ้นที่ต้องการเฝ้าดู
stocks = ['ADVANC.BK', 'TISCO.BK', 'BDMS.BK', 'PTT.BK']

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def check_stocks():
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    report = f"📊 รายงานหุ้นปันผล ({now})\n"
    report += "----------------------------\n"
    
    for symbol in stocks:
        stock = yf.Ticker(symbol)
        # ดึงราคาปัจจุบันและราคาปิดวันก่อน
        df = stock.history(period="2d")
        if not df.empty and len(df) >= 2:
            current_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            change = ((current_price - prev_price) / prev_price) * 100
            
            # ดึงข้อมูลปันผล
            info = stock.info
            div_rate = info.get('dividendRate', 'ไม่มีข้อมูล')
            
            report += f"📌 {symbol}\n"
            report += f"ราคา: {current_price:.2f} ({change:+.2f}%)\n"
            report += f"ปันผลต่อหุ้น: {div_rate} บาท\n"
            report += "----------------------------\n"
        else:
            report += f"❌ {symbol}: ดึงข้อมูลไม่ได้\n"
    
    send_telegram(report)

# สั่งให้ทำงานทันทีทุกครั้งที่รัน
if __name__ == "__main__":
    check_stocks()
