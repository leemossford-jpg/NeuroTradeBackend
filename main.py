from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="NeuroTrade Backend", version="2.0")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for testing (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Finnhub API Key
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# Finnhub base URLs
FINNHUB_QUOTE_URL = "https://finnhub.io/api/v1/quote"
FINNHUB_SYMBOLS_URL = "https://finnhub.io/api/v1/stock/symbol"

@app.get("/")
def root():
    return {"message": "NeuroTrade Backend Online ✅"}

@app.get("/price/{symbol}")
def get_price(symbol: str):
    """Fetch live price for any stock, index, or commodity symbol."""
    try:
        # Support special cases
        aliases = {
            "OIL": "CL=F",  # Crude Oil
            "BRENT": "BZ=F",  # Brent Oil
            "NATGAS": "NG=F",  # Natural Gas
            "GOLD": "GC=F",  # Gold
        }
        symbol = aliases.get(symbol.upper(), symbol.upper())

        url = f"{FINNHUB_QUOTE_URL}?symbol={symbol}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if "c" not in data or data["c"] == 0:
            raise HTTPException(status_code=404, detail="Symbol not found or inactive")

        return {
            "symbol": symbol,
            "current": data["c"],
            "high": data["h"],
            "low": data["l"],
            "open": data["o"],
            "previous_close": data["pc"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/symbols/{exchange}")
def list_symbols(exchange: str = "US"):
    """Get all available symbols for an exchange (default: US)"""
    try:
        url = f"{FINNHUB_SYMBOLS_URL}?exchange={exchange}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch symbols")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
