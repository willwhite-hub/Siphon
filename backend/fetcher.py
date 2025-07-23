from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from commodity_scraper import scrape_commodity
from db import insert_price


PRICE_FILE = Path("prices.json")

def fetch_prices(commodity: str):
    """    
    Fetch the latest price for a given commodity and store it in the database.
    Args:
        commodity (str): The name of the commodity to fetch (e.g., "cotton", "wheat", "barley").
    """
    try:
        data =  scrape_commodity(commodity)
        
        if not data:
            raise ValueError(f"No data found for commodity: {commodity}")
            return

        # Add timestamp to the data
        data["timestamp"] = datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()

        insert_price(
            commodity=data["commodity"],
            price=data["price"],
            change=data["change"],
            currency=data["currency"],
            unit=data["unit"],
            source=data["source"],
            timestamp=data["timestamp"]
        )

        print(f"Successfully fetched and stored price for {data['commodity']}.")

    except Exception as e:
        print(f"Error fetching price for {commodity}: {e}")

