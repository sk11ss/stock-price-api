import numpy as np
import datetime

# --- Anchored VWAP & Fib Retracement helper functions ---
def calculate_anchored_vwap(prices, volumes):
    """
    ✅ Anchored VWAP: (가격 × 거래량) 합 / 거래량 합
    - 단순 placeholder (최근 30일치 데이터로 가정)
    - 향후 Investing.com 또는 TradingView 데이터로 교체 가능
    """
    if not prices or not volumes or len(prices) != len(volumes):
        return None
    return round(np.dot(prices, volumes) / np.sum(volumes), 2)

def calculate_fib_retracement(high, low):
    """
    ✅ Fib Retracement 50~61.8% 눌림목 가격 범위
    - 단순 placeholder: 50% 지점 반환
    """
    fib_50 = low + (high - low) * 0.5
    fib_618 = low + (high - low) * 0.618
    return round((fib_50 + fib_618) / 2, 2)
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

# For external price validation placeholder for web scraping
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"}

def get_latest_price(symbol):
    """
    ✅ Investing.com 웹스크래핑 기반 가격 조회
    """
    try:
        url = f"https://www.investing.com/equities/{symbol.lower()}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            print(f"⚠️ {symbol}: HTTP {res.status_code} 에러")
            return None
        soup = BeautifulSoup(res.text, "html.parser")
        # ✅ Investing.com 가격 CSS selector (동적으로 업데이트 가능)
        price_tag = soup.select_one("div.text-5xl span") or soup.select_one("span.instrument-price_last__KQzyA")
        if price_tag:
            price_text = price_tag.text.replace(",", "").strip()
            return float(price_text)
        else:
            print(f"⚠️ {symbol}: 가격 태그를 찾을 수 없음")
            return None
    except Exception as e:
        print(f"❌ {symbol} 웹스크래핑 에러: {e}")
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
    # 웹스크래핑 기반 즉시 가격 조회 예정
    price = get_latest_price(symbol.upper())
    if price:
        return jsonify({"symbol": symbol.upper(), "price": price, "source": "realtime"})
    else:
        return jsonify({"error": "Realtime price unavailable"}), 404


# TODO: EMA50 endpoint to be rebuilt with scraped historical data or alternate API
# @app.route("/ema50/<symbol>")
# def get_ema50(symbol):
#     return jsonify({"error": "EMA50 calculation not implemented"}), 501

# TODO: Batch prices endpoint to be rebuilt with web scraping
# @app.route("/batch/prices")
# def batch_prices():
#     return jsonify({"error": "Batch prices not implemented"}), 501

# TODO: Batch EMA50 endpoint to be rebuilt with web scraping
# @app.route("/batch/ema50")
# def batch_ema50():
#     return jsonify({"error": "Batch EMA50 not implemented"}), 501

# ✅ 외부 소스 기반 가격 조회 endpoint (웹스크래핑 기반)
@app.route("/external_price/<symbol>")
def get_external_price(symbol):
    """
    ✅ Investing.com 웹스크래핑 기반 가격 조회
    """
    try:
        sym = symbol.upper()
        scraped_price = get_latest_price(sym)
        if scraped_price:
            return jsonify({
                "symbol": sym,
                "price": scraped_price,
                "source": "Investing.com scraping"
            })
        else:
            return jsonify({"error": f"{sym} price not found"}), 404
    except Exception as e:
        return jsonify({"error": f"External price lookup failed: {e}"}), 500

# ✅ 매수표 생성 endpoint
@app.route("/buytable")
def get_buy_table():
    equal_weight = round(100 / len(symbols), 1)

    # --- Placeholder for historical price/volume (실제 데이터 소스 필요) ---
    # 향후 OHLCV 데이터로 교체 예정
    dummy_prices = [100, 102, 105, 103, 104, 106, 108, 107, 109, 110]
    dummy_volumes = [1000, 1200, 1100, 1300, 1250, 1400, 1500, 1600, 1550, 1650]
    high_price = max(dummy_prices)
    low_price = min(dummy_prices)

    table = []
    for sym in symbols:
        current_price = latest_prices.get(sym, None)
        if current_price:
            # ✅ Anchored VWAP (최근 30일 데이터 가정)
            avwap = calculate_anchored_vwap(dummy_prices, dummy_volumes)
            # ✅ Fib Retracement
            fib_price = calculate_fib_retracement(high_price, low_price)

            # ✅ 혼합 추천가: AVWAP -3% 와 Fib 평균치
            avwap_discount = avwap * 0.97 if avwap else current_price * 0.97
            buy_price = round((avwap_discount + fib_price) / 2, 2)

            gap_rate = round(((current_price - buy_price) / buy_price) * 100, 2)
        else:
            buy_price = None
            gap_rate = None

        entry = {
            "종목": SECTOR_MAP.get(sym, sym),
            "구분(분야)": SECTOR_MAP.get(sym, "").split("(")[-1].replace(")", ""),
            "현재가": current_price,
            "매수추천가": buy_price,
            "괴리율(%)": gap_rate,
            "보유": CURRENT_HOLDINGS.get(sym, 0),
            "추가": 0,
            "비중": f"{equal_weight}%"
        }
        table.append(entry)
    return jsonify({"columns": BUY_TABLE_TEMPLATE["columns"], "data": table})

if __name__ == "__main__":
    print("⏳ 1분 단위 가격 수집 + Flask API 시작 (가격 데이터는 웹스크래핑으로 대체 예정)")
    t = threading.Thread(target=collect_prices, daemon=True)
    t.start()
    import os
    port = int(os.environ.get("PORT", 8000))  # Render 포트 환경 변수 사용
    app.run(host="0.0.0.0", port=port)