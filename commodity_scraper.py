import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from currency import get_usd_to_aud
from models import Price
from db import SessionLocal, init_db
from sqlalchemy.orm import Session


def scrape_commodity(commodity: str):
    """
    Scrape the price of a commodity from its respective source.
    Args:
        commodity (str): The name of the commodity to scrape (e.g., "cotton", "wheat", "barley", "beef").
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
    elif commodity.lower() == "beef":
        return scrape_beef()
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
    # Convert price to AUD$/bale
    exchange_rate = get_usd_to_aud()
    if exchange_rate is None:
        raise ValueError("Could not fetch exchange rate for USD to AUD")
    price_aud = round(((price * exchange_rate) / 100) * 500, 2)  # Convert from USc to AUD

    change = cells[1].text.strip()
    change = change.replace("(", "").replace(")", "")  # Remove parentheses
    change = float(change)  # Convert to float
    # Convert change to percentage
    previous_price = price + change
    percentage_change = round((change / previous_price) * 100, 2) if previous_price != 0 else 0.0

    date = datetime.now() # Use current date as publication date

    return {
        "commodity": "Cotton (Cotlook A Index)",
        "price": price_aud,
        "currency": "AUD",
        "change": percentage_change,
        "unit": "$/bale",
        "source": url,
        "timestamp": date,
    }

def scrape_wheat():
    url = "https://www.dpi.nsw.gov.au/agriculture/commodity-report"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WheatScraper/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise error if request fails
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the wheat section
    wheat_section = soup.find("h2", string="Wheat")
    if not wheat_section:
        raise ValueError("Wheat section not found") 
    
    # Go to parent element
    row = wheat_section.find_parent("div", class_="row")
    if not row:
        raise ValueError("Container for wheat price not found")
    container = row.find("div", class_="col-md-8")
    if not container:
        raise ValueError("Container for wheat price not found")
    
    # Extract price
    price_text = container.find("h2").text.strip()
    if not price_text:
        raise ValueError("Price text not found in wheat section")
    price_match = re.search(r"\$(\d+(?:\d+)?)", price_text)
    if not price_match:
        raise ValueError("Price not found in wheat section")
    price = float(price_match.group(1))

    # Extract change
    change_tag = container.find("strong")
    change_text = change_tag.text.strip() if change_tag else ""
    if "steady" in change_text.lower():
        change = 0.0
    else:
        change_match = re.search(r"([+-]?\d+(?:\.\d+)?)%", change_text)
        change = float(change_match.group(1)) if change_match else None
    
    return {
        "commodity": "Wheat (H2)",
        "price": price,
        "currency": "AUD",
        "change": change,
        "unit": "$/tonne",
        "source": url,
        "timestamp": datetime.now(),  # Use current date as publication date
    }

def scrape_barley():
    url = "https://www.dpi.nsw.gov.au/agriculture/commodity-report"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; BarleyScraper/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise error if request fails
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the wheat section
    barley_section = soup.find("h2", string="Barley")
    if not barley_section:
        raise ValueError("Barley section not found") 
    
    # Go to parent element
    row = barley_section.find_parent("div", class_="row")
    if not row:
        raise ValueError("Container for barley price not found")
    container = row.find("div", class_="col-md-8")
    if not container:
        raise ValueError("Container for barley price not found")
    
    # Extract price
    price_text = container.find("h2").text.strip()
    if not price_text:
        raise ValueError("Price text not found in barley section")
    price_match = re.search(r"\$(\d+(?:\.\d+)?)", price_text)
    if not price_match:
        raise ValueError("Price not found in barley section")
    price = float(price_match.group(1))

    # Extract change
    change_tag = container.find("strong")
    change_text = change_tag.text.strip() if change_tag else ""

    if "steady" in change_text.lower():
        change = 0.0
    else:
        change_match = re.search(r"([+-]?\d+(?:\.\d+)?)%", change_text)
        change = float(change_match.group(1)) if change_match else None

    return {
        "commodity": "Barley (feed)",
        "price": price,
        "currency": "AUD",
        "change": change,
        "unit": "$/tonne",
        "source": url,
        "timestamp": datetime.now(), 
    }

def scrape_beef():
    # url for beef prices
    url = "https://www.agriculture.gov.au/abares/data/weekly-commodity-price-update"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; BeefScraper/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise error if request fails

    soup = BeautifulSoup(response.text, "html.parser")

    row = soup.find("td", style="text-align:right;", string="Beef – Eastern Young Cattle Indicator")

    # Extract the next sibling cells
    # date = row.find_next_sibling("td").text
    unit = "c/kg"
    price = row.find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").text
    previous_price = row.find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").text
    # Convert previous price to change
    change  = float(price) - float(previous_price)
    percentage_change = round((change / float(previous_price)) * 100, 2) if float(previous_price) != 0 else 0.0
    
    # Get the date accessed
    date = datetime.now()  # Use current date as publication date

    return {
        "commodity": "Beef (Eastern Young Cattle Indicator)",
        "price": price,
        "currency": "AUD",
        "change": percentage_change,
        "unit": unit,
        "source": url,
        "timestamp": date,
    }

def parse_date(raw_date):
    # Remove 'st', 'nd', 'rd', 'th' from the day part
    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", raw_date)
    return datetime.strptime(cleaned, "%H:%M GMT %d %b, %Y")

# Store data in database
def store_price(data: dict, db: Session):
    # Check for existing entry
    existing = db.query(Price).filter_by(timestamp=data["timestamp"]).first()
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
        data = scrape_commodity("wheat") # Remove this when not testing
        store_price(data, db)
        print("Scraped data:", data)
    except Exception as e:
        print("Error:", e)
    finally:
        db.close()
