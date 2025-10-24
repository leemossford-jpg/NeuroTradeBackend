import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env locally (has no effect on Render; Render uses env vars UI)
load_dotenv()

app = FastAPI()

# CORS: allow everything in dev; lock down later if you want
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("FINNHUB_API_KEY")

@app.get("/")
def root():
    return {"message": "NeuroTrade Backend Online ✅"}

@app.get("/price/{symbol}")
def get_price(symbol: str):
    if not API_KEY:
        return {"error": "FINNHUB_API_KEY missing on server"}

    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()

        # Basic validation
        if "c" not in data or data.get("c") in (None, 0):
            return {"error": "Invalid data from Finnhub (market closed or bad symbol).", "raw": data}

        return {
            "symbol": symbol.upper(),
            "current": data.get("c"),
            "high": data.get("h"),
            "low": data.get("l"),
            "open": data.get("o"),
            "previous_close": data.get("pc"),
        }
    except Exception as e:
        return {"error": f"Failed to fetch: {str(e)}"}
