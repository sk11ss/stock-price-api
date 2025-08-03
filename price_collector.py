import requests
from bs4 import BeautifulSoup
import json
import datetime
import numpy as np
import os

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"}

symbols = ["MSFT", "VRT", "NVDA", "PWR", "GEV", "ORCL", "IONQ", "TSLA", "ASML", "AMD", "AVGO", "SMCI"]

def scrape_ohlcv(symbol):
    """
    ✅ Placeholder for OHLCV scraping – 
    Investing.com에서 30일 OHLCV를 가져오는 자리.
    현재는 dummy data (실제 HTML 파싱 로직 추가 예정).
    """
    dummy_prices = [100, 102, 105, 103, 104, 106, 108, 107, 109, 110] * 3  # 30 days
    dummy_volumes = [1000, 1200, 1100, 1300, 1250, 1400, 1500, 1600, 1550, 1650] * 3
    return dummy_prices, dummy_volumes

def calculate_anchored_vwap(prices, volumes):
    if not prices or not volumes or len(prices) != len(volumes):
        return None
    return round(np.dot(prices, volumes) / np.sum(volumes), 2)

def calculate_fib_retracement(high, low):
    fib_50 = low + (high - low) * 0.5
    fib_618 = low + (high - low) * 0.618
    return round((fib_50 + fib_618) / 2, 2)

def main():
    today = datetime.date.today().strftime("%Y-%m-%d")
    output_file = f"daily_buytable_{today}.json"

    table = []
    for sym in symbols:
        prices, volumes = scrape_ohlcv(sym)
        high_price = max(prices)
        low_price = min(prices)

        avwap = calculate_anchored_vwap(prices, volumes)
        fib_price = calculate_fib_retracement(high_price, low_price)

        avwap_discount = avwap * 0.97 if avwap else None
        buy_price = round((avwap_discount + fib_price) / 2, 2) if avwap_discount and fib_price else None

        entry = {
            "symbol": sym,
            "avwap": avwap,
            "fib_price": fib_price,
            "buy_price": buy_price,
            "calculation_date": today
        }
        table.append(entry)

    with open(output_file, "w") as f:
        json.dump({"date": today, "data": table}, f, indent=2, ensure_ascii=False)

    print(f"✅ Batch completed → {output_file} 생성됨")

if __name__ == "__main__":
    main()