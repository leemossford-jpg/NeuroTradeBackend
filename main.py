from fastapi import FastAPI
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

API_KEY = os.getenv("FINNHUB_API_KEY")

@app.get("/")
def root():
    return {"message": "✅ NeuroTrade Backend Online with Finnhub"}

@app.get("/price/{symbol}")
def get_stock_price(symbol: str):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if "c" not in data or data["c"] == 0:
            return {"error": "Invalid data or market closed."}

        return {
            "symbol": symbol.upper(),
            "current": data.get("c"),
            "high": data.get("h"),
            "low": data.get("l"),
            "open": data.get("o"),
            "previous_close": data.get("pc")
        }
    except Exception as e:
        return {"error": f"Failed to fetch data: {str(e)}"}
