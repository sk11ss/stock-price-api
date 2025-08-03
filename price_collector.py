import yfinance as yf
from flask import Flask, jsonify
import threading
import time

symbols = ["MSFT", "VRT", "NVDA", "PWR", "GEV", "ORCL", "IONQ", "TSLA", "ASML", "AMD", "AVGO"]

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

if __name__ == "__main__":
    print("⏳ 1분 단위 가격 수집 + Flask API 시작")
    t = threading.Thread(target=collect_prices, daemon=True)
    t.start()
    import os
    port = int(os.environ.get("PORT", 8000))  # Render 포트 환경 변수 사용
    app.run(host="0.0.0.0", port=port)