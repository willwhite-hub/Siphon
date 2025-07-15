from fastapi import FastAPI
from contextlib import asynccontextmanager
from pathlib import Path
import json

from fetcher import fetch_prices
from commodity_scraper import scrape_commodity
from datetime import datetime
from zoneinfo import ZoneInfo

PRICE_FILE = Path("prices.json")
SUPPORTED_COMMODITIES = ["cotton", "wheat", "barley"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    all_prices = []
    for commodity in SUPPORTED_COMMODITIES:
        # Fetch prices from the API and scrape data
        try:
            fetch_prices(commodity)
            data = scrape_commodity(commodity)
            data["timestamp"] = datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()
            all_prices.append(data)
        # Handle any errors during fetching or scraping
        except Exception as e:
            print(f"Error during startup fetch for {commodity}: {e}")
    # Write all prices to the JSON file
    with open(PRICE_FILE, "w") as f:
        json.dump(all_prices, f, indent=4)

    yield  # app runs here

    # (Optional) shutdown logic here
# Create the FastAPI app with the lifespan context manager
app = FastAPI(lifespan=lifespan)

@app.get("/")
# Root endpoint
def root():
    return {"message": "Agricultural Price Tracker API"}

@app.get("/prices")
# Endpoint to get all prices
def get_prices():
    if not PRICE_FILE.exists():
        return {"error": "No prices available yet"}
    # Read prices from the JSON file
    with open(PRICE_FILE, "r") as f:
        return json.load(f)
