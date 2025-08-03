from flask import Flask, jsonify
import threading
import requests
import time

API_KEY = "PKFLXCKJJFL57Y9L20TQ"
SECRET_KEY = "qEUwb5wyLkgJswK0STlg2lisDX9TBVGDIOlHTpSc"

symbols = ["MSFT", "VRT", "NVDA", "PWR", "GEV", "ORCL", "IONQ", "TSLA", "ASML", "AMD", "AVGO"]

headers = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY
}

def get_latest_price(symbol):
    url = f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        return data.get("quote", {}).get("ap")  # ask price 사용
    else:
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

if __name__ == "__main__":
    print("⏳ 1분 단위 가격 수집 + Flask API 시작")
    t = threading.Thread(target=collect_prices, daemon=True)
    t.start()
    import os
    port = int(os.environ.get("PORT", 8000))  # Render 포트 환경 변수 사용
    app.run(host="0.0.0.0", port=port)