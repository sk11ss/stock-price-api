import datetime
import yfinance as yf
import json

def collect_prices():
    """
    가격 데이터를 수집하고 가공하여 JSON 파일로 저장하는 함수
    (실제 수집 로직은 여기에 작성)
    """
    print("📊 Starting daily price collection...")
    today = datetime.date.today()

    tickers = ["MSFT", "NVDA", "ORCL", "AVGO", "SMCI", "VRT", "PWR", "GEV", "IONQ", "TSLA", "AMD", "ASML"]
    prices = {}

    for ticker in tickers:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            prices[ticker] = price
            print(f"{ticker}: {price}")
        else:
            print(f"{ticker}: No data available")

    filename = f"daily_buytable_{today}.json"
    with open(filename, 'w') as f:
        json.dump(prices, f, indent=4)

    print(f"✅ Price collection completed for {today}")

if __name__ == "__main__":
    collect_prices()
