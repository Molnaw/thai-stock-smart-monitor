import yfinance as yf
import requests
from datetime import datetime
import pytz

# --- ข้อมูลการเชื่อมต่อ ---
TOKEN = "7508299140:AAGpdtv8z_ZBUB1eTT7DKwjTqUMFZ8xQJmE"
CHAT_ID = "8178648877"

# รายชื่อหุ้นแยกกลุ่ม
stocks_new = ['ADVANC.BK', 'TISCO.BK', 'BDMS.BK', 'PTT.BK'] # ชุดใหม่
stocks_old = ['SIRI.BK', 'BTS.BK', 'TWPC.BK']              # ชุดเก่า

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, json=payload)

def get_stock_report(stock_list, title):
    now = datetime.now(pytz.timezone('Asia/Bangkok')).strftime("%d/%m/%Y %H:%M")
    report = f"📊 {title} ({now})\n"
    report += "----------------------------\n"
    for symbol in stock_list:
        stock = yf.Ticker(symbol)
        df = stock.history(period="2d")
        if not df.empty and len(df) >= 2:
            current_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            change = ((current_price - prev_price) / prev_price) * 100
            report += f"📌 {symbol}: {current_price:.2f} ({change:+.2f}%)\n"
    return report

if __name__ == "__main__":
    # ตั้งค่าเวลาไทย
    tz = pytz.timezone('Asia/Bangkok')
    now_hour = datetime.now(tz).hour

    # --- ตั้งเงื่อนไขเวลาที่นี่ ---
    
    # 1. ถ้าเป็นเวลา 10 โมงเช้า ให้ส่งรายงานหุ้น "ชุดใหม่"
    if now_hour == 10:
        msg = get_stock_report(stocks_new, "รายงานหุ้นปันผล (ชุดใหม่)")
        send_telegram(msg)
        
    # 2. ถ้าเป็นเวลา 17 โมงเย็น (5 โมง) ให้ส่งรายงานหุ้น "ชุดเก่า"
    elif now_hour == 17:
        msg = get_stock_report(stocks_old, "รายงานหุ้นเดิม (ชุดเก่า)")
        send_telegram(msg)
    
    # 3. พิเศษ: ถ้าคุณกดรันเอง (Manual Run) ในช่วงเวลาอื่น ให้ส่งทั้งคู่มาเลยเพื่อทดสอบ
    else:
        msg_new = get_stock_report(stocks_new, "ทดสอบรันเอง: หุ้นชุดใหม่")
        msg_old = get_stock_report(stocks_old, "ทดสอบรันเอง: หุ้นชุดเก่า")
        send_telegram(msg_new)
        send_telegram(msg_old)
