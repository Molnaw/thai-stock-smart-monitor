import yfinance as yf
import requests
from datetime import datetime

# --- ข้อมูลการเชื่อมต่อที่คุณให้มาใหม่ ---
TOKEN = "7508299140:AAGpdtv8z_ZBUB1eTT7DKwjTqUMFZ8xQJmE"
CHAT_ID = "8178648877"

# รายชื่อหุ้นเป้าหมาย
stocks = ['ADVANC.BK', 'TISCO.BK', 'BDMS.BK', 'PTT.BK']

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ ส่งข้อความสำเร็จ!")
        else:
            print(f"❌ ส่งไม่สำเร็จ: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def check_stocks():
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    report = f"📊 รายงานหุ้นปันผล ({now})\n"
    report += "----------------------------\n"
    
    for symbol in stocks:
        stock = yf.Ticker(symbol)
        # ดึงราคาปัจจุบัน
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

# สั่งให้ทำงานทันทีทุกครั้งที่กดรัน
if __name__ == "__main__":
    check_stocks()
