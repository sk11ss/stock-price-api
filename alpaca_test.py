import requests

API_KEY = "PKFLXCKJJFL57Y9L20TQ"
SECRET_KEY = "qEUwb5wyLkgJswK0STlg2lisDX9TBVGDIOlHTpSc"

url = "https://data.alpaca.markets/v2/stocks/AAPL/quotes/latest"

headers = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY
}

r = requests.get(url, headers=headers)

print("Status Code:", r.status_code)

try:
    print("Response:", r.json())
except Exception:
    print("Response (raw):", r.text)