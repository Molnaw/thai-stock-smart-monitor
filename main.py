import yfinance as yf
import requests
from datetime import datetime
import pytz

# --- ข้อมูลการเชื่อมต่อ ---
TOKEN = "7508299140:AAGpdtv8z_ZBUB1eTT7DKwjTqUMFZ8xQJmE"
CHAT_ID = "8178648877"

# --- ตั้งค่าพอร์ตหุ้นของคุณ (แก้ไขตัวเลข จำนวนหุ้น และ ต้นทุน ตรงนี้ได้เลยครับ) ---
my_portfolio = {
    # หุ้นชุดเดิม
    'SIRI.BK': {'vol': 1000, 'avg': 1.40}, 
    'BTS.BK':  {'vol': 500,  'avg': 9.02},
    'TWPC.BK': {'vol': 200,  'avg': 11.42},
    
    # หุ้นปันผลชุดใหม่ (ถ้ายังไม่มีในพอร์ต ให้ใส่ vol เป็น 0 ไว้ก่อนครับ)
    'ADVANC.BK': {'vol': 0, 'avg': 0},
    'TISCO.BK':  {'vol': 0, 'avg': 0},
    'BDMS.BK':   {'vol': 0, 'avg': 0},
    'PTT.BK':    {'vol': 0, 'avg': 0}
}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def get_portfolio_report(stock_list, title):
    now = datetime.now(pytz.timezone('Asia/Bangkok')).strftime("%d/%m/%Y %H:%M")
    report = f"📊 *{title}* \n({now})\n"
    report += "----------------------------\n"
    
    for symbol in stock_list:
        stock = yf.Ticker(symbol)
        df = stock.history(period="1d")
        if not df.empty:
            curr = df['Close'].iloc[-1]
            vol = my_portfolio[symbol]['vol']
            avg = my_portfolio[symbol]['avg']
            
            report += f"📌 *{symbol}*\n"
            report += f"ราคา: {curr:.2f} "
            
            # ถ้ามีหุ้นในพอร์ต ให้คำนวณกำไร/ขาดทุน
            if vol > 0:
                profit_pct = ((curr - avg) / avg) * 100
                profit_amt = (curr - avg) * vol
                emoji = "🟢" if profit_amt >= 0 else "🔴"
                report += f"(ทุน: {avg:.2f})\n"
                report += f"{emoji} กำไร/ขาดทุน: {profit_pct:+.2f}% ({profit_amt:,.2f} บาท)\n"
            else:
                # ถ้าไม่มีหุ้น ให้โชว์แค่ราคาและปันผล (สำหรับหุ้นชุดใหม่)
                info = stock.info
                div = info.get('dividendRate', 0)
                report += f"\n💰 ปันผล: {div} บาท/หุ้น\n"
            
            report += "----------------------------\n"
    return report

if __name__ == "__main__":
    tz = pytz.timezone('Asia/Bangkok')
    now_hour = datetime.now(tz).hour

    # รายชื่อหุ้นแต่ละกลุ่ม
    old_list = ['SIRI.BK', 'BTS.BK', 'TWPC.BK']
    new_list = ['ADVANC.BK', 'TISCO.BK', 'BDMS.BK', 'PTT.BK']

    # ตั้งเวลาส่ง
    if now_hour == 10:
        msg = get_portfolio_report(new_list, "รายงานหุ้นปันผลเป้าหมาย")
        send_telegram(msg)
    elif now_hour == 17 or now_hour == 18 or now_hour == 19:
        msg = get_portfolio_report(old_list, "รายงานพอร์ตหุ้นปัจจุบัน")
        send_telegram(msg)
    else:
        # ถ้ากดรันเอง ให้ส่งสรุปทั้ง 2 ชุด
        send_telegram(get_portfolio_report(new_list, "สรุปหุ้นเป้าหมาย (Manual)"))
        send_telegram(get_portfolio_report(old_list, "สรุปพอร์ตจริง (Manual)"))
