import yfinance as yf
import requests
from datetime import datetime
import pytz

# --- ข้อมูลการเชื่อมต่อ ---
TOKEN = "7508299140:AAGpdtv8z_ZBUB1eTT7DKwjTqUMFZ8xQJmE"
CHAT_ID = "8178648877"

# --- ข้อมูลพอร์ตหุ้นของคุณ (แก้ไขตรงนี้ได้ถ้าจำนวนหุ้นเปลี่ยน) ---
my_portfolio = {
    'SIRI.BK': {'vol': 1000, 'avg': 1.40}, 
    'BTS.BK':  {'vol': 500,  'avg': 9.02},
    'TWPC.BK': {'vol': 200,  'avg': 11.42},
    'ADVANC.BK': {'vol': 0, 'avg': 0},
    'TISCO.BK':  {'vol': 0, 'avg': 0},
    'BDMS.BK':   {'vol': 0, 'avg': 0},
    'PTT.BK':    {'vol': 0, 'avg': 0}
}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def generate_report():
    tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(tz).strftime("%d/%m/%Y %H:%M")
    
    report = f"🚀 *รายงานสรุปหุ้นทั้งหมด*\n📅 {now}\n"
    report += "━━━━━━━━━━━━━━━━━━\n"
    
    # วนลูปเช็คหุ้นทุกตัวในพอร์ต
    for symbol, data in my_portfolio.items():
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period="2d")
            if df.empty: continue
            
            curr = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2]
            change = ((curr - prev) / prev) * 100
            
            report += f"📌 *{symbol}*\n"
            report += f"ราคา: {curr:.2f} ({change:+.2f}%)\n"
            
            # ถ้ามีหุ้น (vol > 0) ให้โชว์กำไร/ขาดทุน
            if data['vol'] > 0:
                profit_pct = ((curr - data['avg']) / data['avg']) * 100
                profit_amt = (curr - data['avg']) * data['vol']
                emoji = "🟢" if profit_amt >= 0 else "🔴"
                report += f"{emoji} กำไร/ขาดทุน: {profit_pct:+.2f}% ({profit_amt:,.2f} บาท)\n"
            else:
                # ถ้าไม่มีหุ้น ให้โชว์เงินปันผลแทน
                info = stock.info
                div = info.get('dividendRate', 0)
                report += f"💰 ปันผล: {div if div else 'รอข้อมูล'} บาท/หุ้น\n"
                
            report += "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
        except:
            report += f"❌ {symbol}: ดึงข้อมูลไม่ได้\n"
            
    send_telegram(report)

if __name__ == "__main__":
    generate_report()
