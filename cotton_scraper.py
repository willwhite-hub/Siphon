import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path


def scrape_cotton_price():
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
    change = round(float(change), 2)  # Convert to float

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
        pub_date = datetime.strptime(pub_date_raw, "%H:%M GMT %d%b, %Y")
    except ValueError:
        pub_date = pub_date_raw  # fallback to raw string if parsing fails

    return {
        "commodity": "Cotton Price (Cotlook A Index)",
        "price": price,
        "change": (change / price) * 100,
        "published_at": pub_date,
        "source": url,
    }


# Append mode: write header only if file doesn't 

# Run test
if __name__ == "__main__":
    try:
        data = scrape_cotton_price()
        print("Scraped data:", data)
    except Exception as e:
        print("Error:", e)
