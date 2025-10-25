from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "d3t6v41r01qqdgfugm40d3t6v41r01qqdgfugm4g")
BASE_URL = "https://finnhub.io/api/v1"

@app.get("/")
def home():
    return {"message": "NeuroTrade Backend Online ✅"}

# Detect asset type and return appropriate endpoint
def detect_asset_type(symbol: str):
    if "/" in symbol:
        return "forex"
    elif symbol.upper() in ["NG", "CL", "GC", "SI"]:
        return "commodity"
    elif symbol.upper().startswith("^"):
        return "index"
    elif symbol.upper() in ["BTCUSD", "ETHUSD"]:
        return "crypto"
    else:
        return "stock"

@app.get("/price/{symbol}")
def get_price(symbol: str):
    try:
        asset_type = detect_asset_type(symbol)
        symbol = symbol.upper().strip()

        if asset_type == "stock":
            url = f"{BASE_URL}/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        elif asset_type == "forex":
            url = f"{BASE_URL}/quote?symbol=OANDA:{symbol}&token={FINNHUB_API_KEY}"
        elif asset_type == "crypto":
            url = f"{BASE_URL}/crypto/candle?symbol=BINANCE:{symbol}&resolution=1&count=1&token={FINNHUB_API_KEY}"
        elif asset_type == "commodity":
            url = f"{BASE_URL}/quote?symbol={symbol}=COM&token={FINNHUB_API_KEY}"
        elif asset_type == "index":
            url = f"{BASE_URL}/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        else:
            return {"error": "Unknown asset type"}

        r = requests.get(url)
        data = r.json()

        if "c" in data:
            return {
                "symbol": symbol,
                "current": data["c"],
                "high": data["h"],
                "low": data["l"],
                "open": data["o"],
                "previous_close": data["pc"],
                "type": asset_type,
            }
        else:
            return {"error": "Invalid response", "details": data}

    except Exception as e:
        return {"error": str(e)}
