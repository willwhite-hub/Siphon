from fastapi import FastAPI
import json
from pathlib import Path

app = FastAPI()

PRICE_FILE = Path("prices.json")

@app.get("/")
def root():
    return {"message": "Cotton Price Tracker API"}

@app.get("/prices")
def get_prices():
    if not PRICE_FILE.exists():
        return {"error": "No prices avaiable yet"}
    
    with open(PRICE_FILE, "r") as f:
        data = json.load(f)

    return data