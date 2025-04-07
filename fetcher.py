import requests
import json
from datetime import datetime
from pathlib import Path

PRICE_FILE = Path("prices.json")


def fetch_cotton_price():
    # Simulated price API response
    # Replace with read API or scrape source
    price_data = {
        "commodity": "Cotton",
        "price": "450.69",  # AUD/bale
        "currency": "AUD",
        "unit": "dollars/bale",
        "source": "source.net",  # example
        "timestamp": datetime.now().isoformat(),
    }

    # Save to file (could be DB in future)
    with open(PRICE_FILE, "w") as f:
        json.dump(price_data, f, indent=4)

    print("Fetched and saved latest cotton price.")


if __name__ == "__main__":
    fetch_cotton_price()
