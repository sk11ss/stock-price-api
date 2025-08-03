from alpaca_trade_api.stream import Stream

API_KEY = "PKFLXCKJJFL57Y9L20TQ"
SECRET_KEY = "qEUwb5wyLkgJswK0STlg2lisDX9TBVGDIOlHTpSc"
BASE_URL = "https://paper-api.alpaca.markets"
DATA_FEED = "iex"

latest_prices = {}

async def trade_callback(data):
    latest_prices[data.symbol] = data.price
    print(f"[{data.symbol}] {data.price}")

def start_ws():
    stream = Stream(API_KEY, SECRET_KEY, base_url=BASE_URL, data_feed=DATA_FEED)
    
    # ✅ 여기에 원하는 심볼을 리스트로 한 번에 적기
    symbols = ["MSFT", "VRT", "NVDA", "PWR", "GEV", "ORCL", "CLS", "HOOD", "IONQ", "TSLA"]
    
    for sym in symbols:
        stream.subscribe_trades(trade_callback, sym)
    
    stream.run()

if __name__ == "__main__":
    start_ws()