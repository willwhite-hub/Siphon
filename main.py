from fastapi import FastAPI
from contextlib import asynccontextmanager
from pathlib import Path
import json

from fetcher import fetch_and_store_price
from commodity_scraper import scrape_commodity
from datetime import datetime

PRICE_FILE = Path("prices.json")
SUPPORTED_COMMODITIES = ["cotton", "wheat", "barley"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    all_prices = []
    for commodity in SUPPORTED_COMMODITIES:
        try:
            fetch_and_store_price(commodity)
            data = scrape_commodity(commodity)
            data["timestamp"] = datetime.utcnow().isoformat()
            all_prices.append(data)
        except Exception as e:
            print(f"Error during startup fetch for {commodity}: {e}")

    with open(PRICE_FILE, "w") as f:
        json.dump(all_prices, f, indent=4)

    yield  # app runs here

    # (Optional) shutdown logic here

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Agricultural Price Tracker API"}

@app.get("/prices")
def get_prices():
    if not PRICE_FILE.exists():
        return {"error": "No prices available yet"}

    with open(PRICE_FILE, "r") as f:
        return json.load(f)
