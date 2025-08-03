import requests

url = "https://paper-api.alpaca.markets/v2/account"
headers = {
    "APCA-API-KEY-ID": "PKNAPMV01P0FEZZC6X6I",
    "APCA-API-SECRET-KEY": "43VDfqjjJvJ2lhZtkYseGYpxVaRykPRizPzfW"
}
r = requests.get(url, headers=headers)
print(r.status_code)
print(r.text)