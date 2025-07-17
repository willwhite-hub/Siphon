import json
from contextlib import asynccontextmanager
from pathlib import Path
from fetcher import fetch_prices
from commodity_scraper import scrape_commodity
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Price
from fastapi import Depends
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PRICE_FILE = Path("prices.json")
SUPPORTED_COMMODITIES = ["cotton", "wheat", "barley", "beef"]


def get_db():
    """
    Dependency to get a database session.
    Yields:
        Session: A SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to initialize the app and fetch initial prices.
    This runs once when the app starts up.
    Args:   
        app (FastAPI): The FastAPI application instance.        
        Yields:
            None: The app is running.
    """
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

# Enable CORS
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Add route for historical data
@app.get("/history/{commodity}")
def get_historical_prices(commodity: str, db: Session = Depends(get_db)):
    """
    Get historical prices for a specific commodity.
    Args:
        commodity (str): The commodity to fetch historical prices for.
       db (Session): The database session.
    Returns:
        List[Price]: A list of historical prices for the commodity.
    """
    results = db.query(Price)\
        .filter(Price.commodity.ilike(f"%{commodity}%"))\
        .order_by(Price.timestamp.desc())\
        .all()
    
    # Convert SQLAlchemy results to dictionaries
    return [
        {
            "commodity": r.commodity,
            "price": r.price,
            "currency": r.currency,
            "change": r.change,
            "unit": r.unit,
            "source": r.source,
            "timestamp": r.timestamp.isoformat(),
            
        } for r in results
    ]