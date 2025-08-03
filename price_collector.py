import yfinance as yf
from flask import Flask, jsonify
import threading
import time

symbols = ["MSFT", "VRT", "NVDA", "PWR", "GEV", "ORCL", "IONQ", "TSLA", "ASML", "AMD", "AVGO", "SMCI"]

# ✅ 매수표 템플릿 (고정)
# 1열: 종목, 2열: 구분(분야), 3열: 현재가, 4열: 매수추천가, 5열: 괴리율, 6열: 보유, 7열: 추가, 8열: 비중
BUY_TABLE_TEMPLATE = {
    "columns": ["종목", "구분(분야)", "현재가", "매수추천가", "괴리율(%)", "보유", "추가", "비중"],
    "description": "종목명은 예: MSFT (Azure/AI), 구분(분야)은 AI 섹터의 분야 표기, 보유/추가 주식수 포함"
}

# ✅ 매수표 기본 구조 (데이터 예시 없이 템플릿만)

BUY_TABLE_DATA = [
    {"구분": "", "종목": "", "현재가": 0.0, "매수추천가": 0.0, "괴리율(%)": 0.0, "보유": 0, "추가": 0, "비중": "0%"}
    # ✅ 실제 데이터는 별도 로직에서 추가됨
]

# ✅ 심볼별 AI 섹터 구분
SECTOR_MAP = {
    "MSFT": "MSFT (Azure/AI)",
    "ORCL": "ORCL (DB)",
    "NVDA": "NVDA (GPU)",
    "AMD": "AMD (CPU)",
    "AVGO": "AVGO (Network)",      # AVGO → 반도체 장비로 간주
    "SMCI": "SMCI (Server)",
    "ASML": "ASML (EUV)",          # ASML → 반도체 장비로 간주
    "PWR": "PWR (AI 전력)",         # 전력 → AI 전력
    "VRT": "VRT (냉각)",
    "GEV": "GEV (AI 전력)",         # 전력 → AI 전력
    "IONQ": "IONQ (양자컴)",
    "TSLA": "TSLA (로보틱스)"
}

# ✅ 현재 보유 주식 수
CURRENT_HOLDINGS = {
    "MSFT": 8,
    "NVDA": 20,
    "ORCL": 12,
    "AVGO": 5,
    "VRT": 18,
    "PWR": 5,
    "GEV": 4,
    "SMCI": 26,
    "IONQ": 115,
    "ASML": 0,
    "AMD": 0,
    "TSLA": 0
}

def get_latest_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        return ticker.info.get("regularMarketPrice")
    except Exception as e:
        print(f"yfinance error for {symbol}: {e}")
        return None

latest_prices = {}

def collect_prices():
    global latest_prices
    while True:
        for sym in symbols:
            price = get_latest_price(sym)
            if price:
                latest_prices[sym] = price
                print(f"💹 {sym}: {price}")
            else:
                print(f"⚠️ {sym}: 가격 조회 실패")
        print("-" * 40)
        time.sleep(60)

app = Flask(__name__)

@app.route("/price/<symbol>")
def get_price(symbol):
    price = latest_prices.get(symbol.upper())
    if price:
        return jsonify({"symbol": symbol.upper(), "price": price})
    else:
        return jsonify({"error": "No data yet"}), 404

@app.route("/price/realtime/<symbol>")
def get_price_realtime(symbol):
    # Yahoo Finance에서 즉시 가격 조회
    price = get_latest_price(symbol.upper())
    if price:
        return jsonify({"symbol": symbol.upper(), "price": price, "source": "realtime"})
    else:
        return jsonify({"error": "Realtime price unavailable"}), 404


# EMA50 endpoint
@app.route("/ema50/<symbol>")
def get_ema50(symbol):
    symbol = symbol.upper()
    try:
        data = yf.download(symbol, period="6mo", interval="1d")
        if not data.empty:
            ema50 = data['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
            return jsonify({"symbol": symbol, "ema50": round(ema50, 2)})
        else:
            return jsonify({"error": "No data for EMA50"}), 404
    except Exception as e:
        return jsonify({"error": f"EMA50 calculation failed: {e}"}), 500


# Batch prices endpoint
@app.route("/batch/prices")
def batch_prices():
    results = {}
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            price = ticker.info.get("regularMarketPrice")
            results[sym] = round(price, 2) if price else None
        except Exception as e:
            results[sym] = None
    return jsonify(results)

# Batch EMA50 endpoint
@app.route("/batch/ema50")
def batch_ema50():
    results = {}
    for sym in symbols:
        try:
            data = yf.download(sym, period="6mo", interval="1d")
            if not data.empty:
                ema50 = data['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
                results[sym] = round(ema50, 2)
            else:
                results[sym] = None
        except Exception as e:
            results[sym] = None
    return jsonify(results)

# ✅ 매수표 생성 endpoint
@app.route("/buytable")
def get_buy_table():
    table = []
    for sym in symbols:
        current_price = latest_prices.get(sym, None)
        ema50 = None
        buy_price = None
        gap_rate = None
        try:
            data = yf.download(sym, period="6mo", interval="1d")
            if not data.empty:
                ema50 = data['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
                buy_price = round(ema50 * 0.97, 2)
                if current_price:
                    gap_rate = round(((buy_price - current_price) / current_price) * 100, 2)
        except Exception as e:
            ema50 = None

        entry = {
            "종목": SECTOR_MAP.get(sym, sym),
            "구분(분야)": SECTOR_MAP.get(sym, "").split("(")[-1].replace(")", ""),
            "현재가": current_price,
            "매수추천가": buy_price,
            "괴리율(%)": gap_rate,
            "보유": CURRENT_HOLDINGS.get(sym, 0),
            "추가": 0,
            "비중": "0%"
        }
        table.append(entry)
    return jsonify({"columns": BUY_TABLE_TEMPLATE["columns"], "data": table})

if __name__ == "__main__":
    print("⏳ 1분 단위 가격 수집 + Flask API 시작")
    t = threading.Thread(target=collect_prices, daemon=True)
    t.start()
    import os
    port = int(os.environ.get("PORT", 8000))  # Render 포트 환경 변수 사용
    app.run(host="0.0.0.0", port=port)