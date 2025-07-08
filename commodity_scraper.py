import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

from models import Price
from db import SessionLocal, init_db
from sqlalchemy.orm import Session


def scrape_commodity(commodity: str):
    """
    Scrape the price of a commodity from its respective source.
    Args:
        commodity (str): The name of the commodity to scrape (e.g., "cotton", "wheat", "barley").
    Returns:
        dict: A dictionary containing the scraped price data.
    Raises:
        ValueError: If the commodity is not supported.
    """
    if commodity.lower() == "cotton":
        return scrape_cotton()
    elif commodity.lower() == "wheat":
        return scrape_wheat()
    elif commodity.lower() == "barley":
        return scrape_barley()
    else:
        raise ValueError(f"Unsupported commodity: {commodity}")


# Scrape cotton price from Cotlook A Index
def scrape_cotton():
    url = "https://www.cotlook.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; CottonScraper/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise error if request fails

    soup = BeautifulSoup(response.text, "html.parser")

    # Get the A Index row
    row = soup.find("tr", id="aIndex")
    if not row:
        raise ValueError("A Index row not found")

    cells = row.find_all("td")
    if len(cells) < 2:
        raise ValueError("Not enough cells in A Index row")

    price = float(cells[0].text.strip())
    change = cells[1].text.strip()
    change = change.replace("(", "").replace(")", "")  # Remove parentheses
    change = float(change)  # Convert to float

    # Get the date following the specific span
    date_span = soup.find(
        "span", class_="show-for-sr", string=". Date of index value: "
    )
    if not date_span:
        raise ValueError("Date span not found")

    # The actual date is in the next sibling text node
    pub_date_raw = date_span.next_sibling.strip()

    # Optional: parse the date into a datetime object
    try:
        pub_date = parse_date(pub_date_raw)
    except ValueError:
        raise ValueError(
            f"Could not parse date: {pub_date_raw}"
        )  # fallback to raw string if parsing fails

    return {
        "commodity": "Cotton Price (Cotlook A Index)",
        "price": price,
        "currency": "AUD",
        "change": change,
        "unit": "$/bale",
        "source": url,
        "timestamp": pub_date,
    }


def scrape_wheat():
    # TODO: Implement wheat scraping logic
    return {
        "commodity": "Wheat Price",
        "price": 0.0,
        "currency": "AUD",
        "change": 0.0,
        "unit": "$/tonne",
        "source": "https://example.com/wheat",
        "timestamp": "pub_date",
    }


def scrape_barley():
    # TODO: Implement barley scraping logic
    return {
        "commodity": "Barley Price",
        "price": 0.0,
        "currency": "AUD",
        "change": 0.0,
        "unit": "$/tonne",
        "source": "https://example.com/barley",
        "timestamp": "pub_date",
    }


def parse_date(raw_date):
    # Remove 'st', 'nd', 'rd', 'th' from the day part
    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", raw_date)
    return datetime.strptime(cleaned, "%H:%M GMT %d %b, %Y")


# Store data in database
def store_price(data: dict, db: Session):
    # Check for existing entry
    existing = db.query(Price).filter_by(published_at=data["published_at"]).first()
    if existing:
        print("Entry for this date already exists.")
        return

    new_entry = Price(**data)
    db.add(new_entry)
    db.commit()
    print("Stored price in database.")


# Run test
if __name__ == "__main__":
    init_db()
    db = SessionLocal()

    try:
        data = scrape_commodity()
        store_price(data, db)
        print("Scraped data:", data)
    except Exception as e:
        print("Error:", e)
    finally:
        db.close()
