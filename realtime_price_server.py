from alpaca_trade_api.stream import Stream
from flask import Flask, jsonify
import threading

# 🔑 Alpaca API 정보
API_KEY = "PKFLXCKJJFL57Y9L20TQ"
SECRET_KEY = "qEUwb5wyLkgJswK0STlg2lisDX9TBVGD"
BASE_URL = "https://paper-api.alpaca.markets"

# 📊 무료 데이터 피드 (Paper 계정은 'iex'만 사용 가능)
DATA_FEED = "iex"

# 📈 포트폴리오 종목 (원하면 확장 가능)
symbols = ["MSFT", "VRT", "NVDA", "PWR", "GEV", "ORCL", "CLS", "HOOD"]

# ✅ 최신 가격 저장할 딕셔너리
latest_prices = {}

# ✅ Flask 앱 생성
app = Flask(__name__)

@app.route("/price/<symbol>")
def get_price(symbol):
    """ 심볼(symbol) 현재 가격을 반환 """
    price = latest_prices.get(symbol.upper())
    if price:
        return jsonify({"symbol": symbol.upper(), "price": price})
    else:
        return jsonify({"error": "No data for this symbol yet"}), 404

# ✅ Alpaca WebSocket 콜백 함수
async def trade_callback(data):
    latest_prices[data.symbol] = data.price

# ✅ Alpaca WebSocket 실행 함수
def start_websocket():
    stream = Stream(API_KEY, SECRET_KEY, base_url=BASE_URL, data_feed=DATA_FEED)
    for sym in symbols:
        stream.subscribe_trades(trade_callback, sym)
    stream.run()

# ✅ Flask 서버와 WebSocket을 동시에 실행
if __name__ == "__main__":
    # WebSocket 스레드 시작
    t = threading.Thread(target=start_websocket)
    t.start()

    # Flask 서버 시작
    app.run(host="0.0.0.0", port=8000)