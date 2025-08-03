from flask import Flask, jsonify
from ws_collector import latest_prices

app = Flask(__name__)

@app.route("/price/<symbol>")
def get_price(symbol):
    price = latest_prices.get(symbol.upper())
    if price:
        return jsonify({"symbol": symbol.upper(), "price": price})
    else:
        return jsonify({"error": "No data yet"}), 404

if __name__ == "__main__":
    app.run(port=8000)