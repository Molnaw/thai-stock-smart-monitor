import yfinance as yf
import requests
from datetime import datetime
import pytz
import time

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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=15)

def fetch_price_yahoo_direct(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d"
    res = requests.get(url, headers=HEADERS, timeout=15)
    res.raise_for_status()
    data = res.json()
    result = (data.get("chart", {}).get("result") or [None])[0]
    if not result:
        return None, None
    closes = (result.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
    valid_closes = [c for c in closes if c is not None]
    if len(valid_closes) >= 2:
        return float(valid_closes[-1]), float(valid_closes[-2])
    elif len(valid_closes) == 1:
        meta_prev = result.get("meta", {}).get("chartPreviousClose")
        prev_val = float(meta_prev) if meta_prev is not None else float(valid_closes[-1])
        return float(valid_closes[-1]), prev_val
    return None, None

def fetch_stock_prices(symbol):
    # 1) ลองดึงผ่าน Yahoo Chart API โดยตรงก่อน
    try:
        curr, prev = fetch_price_yahoo_direct(symbol)
        if curr is not None and prev is not None and prev != 0:
            return curr, prev
    except Exception:
        pass

    # 2) สำรองด้วย yfinance.Ticker
    stock = yf.Ticker(symbol)
    df = stock.history(period="5d")
    if df is not None and not df.empty:
        closes = df['Close'].dropna()
        if len(closes) >= 2:
            return float(closes.iloc[-1]), float(closes.iloc[-2])
        elif len(closes) == 1:
            return float(closes.iloc[-1]), float(closes.iloc[-1])

    raise ValueError(f"No price data for {symbol}")

def fetch_dividend_rate(symbol):
    try:
        info = yf.Ticker(symbol).info or {}
        div = info.get('dividendRate')
        if div is not None and float(div) > 0:
            return f"{float(div):.2f}"
    except Exception:
        pass
    return "รอข้อมูล"

def generate_report():
    tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(tz).strftime("%d/%m/%Y %H:%M")
    
    report = f"🚀 *รายงานสรุปหุ้นทั้งหมด*\n📅 {now}\n"
    report += "━━━━━━━━━━━━━━━━━━\n"
    
    # วนลูปเช็คหุ้นทุกตัวในพอร์ต
    for symbol, data in my_portfolio.items():
        try:
            curr, prev = fetch_stock_prices(symbol)
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
                div_text = fetch_dividend_rate(symbol)
                report += f"💰 ปันผล: {div_text} บาท/หุ้น\n"
                
            report += "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
            time.sleep(0.5)
        except Exception:
            report += f"❌ {symbol}: ดึงข้อมูลไม่ได้\n"
            
    send_telegram(report)

if __name__ == "__main__":
    generate_report()
