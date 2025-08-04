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
    if commodity.lower() == "cotlook_a_index":
        return scrape_cotton()
    elif commodity.lower() == "cotton_futures":
        return scrape_cotton_futures()
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

def scrape_cotton_futures():
    """
    Scrape the 5 most recent cotton futures contracts including cash from Barchart.
    Returns a list of contract data.
    """
    from datetime import datetime as dt
    
    # Cotton futures trade with contract months: March (H), May (K), July (N), October (V), December (Z)
    current_month = dt.now().month
    current_year = dt.now().year % 100  # Get last 2 digits of year
    next_year = (current_year + 1) % 100
    
    # Define the contract month codes and their corresponding months
    contract_months = [
        (3, "H"),   # March
        (5, "K"),   # May
        (7, "N"),   # July
        (10, "V"),  # October
        (12, "Z")   # December
    ]
    
    # Build list of 5 most recent contracts including cash
    contracts_to_scrape = []
    
    # Add cash/spot contract
    contracts_to_scrape.append(("Cotton Cash", "https://www.barchart.com/futures/quotes/cotton"))
    
    # Generate next 4 contract months
    contracts_added = 0
    year_to_check = current_year
    
    for _ in range(2):  # Check current and next year
        for month_num, month_code in contract_months:
            if contracts_added >= 4:  # We want 4 futures + 1 cash = 5 total
                break
                
            # Only add contracts that are in the future or current month
            if year_to_check == current_year and month_num < current_month:
                continue
                
            symbol = f"CT{month_code}{year_to_check:02d}"
            url = f"https://www.barchart.com/futures/quotes/{symbol}"
            contracts_to_scrape.append((f"Cotton {month_code}{year_to_check:02d}", url))
            contracts_added += 1
            
        year_to_check = next_year
        if contracts_added >= 4:
            break
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    def scrape_single_contract(contract_name, url):
        """Scrape a single cotton contract"""
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text()
            
            price_data = None
            change_data = None
            change_percent = None
            
            # Method 1: Look for "Last Price" pattern in text
            last_price_match = re.search(r'Last Price[:\s]*([0-9]+\.?[0-9]*)', page_text, re.IGNORECASE)
            if last_price_match:
                potential_price = float(last_price_match.group(1))
                if 40 < potential_price < 200:  # Reasonable cotton price range in cents
                    price_data = potential_price
            
            # Method 2: Look for price patterns in the text content
            if not price_data:
                price_patterns = re.findall(r'([0-9]{2,3}\.[0-9]{1,2})[s]?', page_text)
                for price_str in price_patterns:
                    potential_price = float(price_str)
                    if 40 < potential_price < 200:
                        price_data = potential_price
                        break
            
            # Method 3: Look in specific HTML elements
            if not price_data:
                for tag in ['span', 'div', 'td']:
                    elements = soup.find_all(tag, string=re.compile(r'[0-9]{2,3}\.[0-9]{2}'))
                    for elem in elements:
                        text = elem.get_text(strip=True)
                        price_match = re.search(r'([0-9]{2,3}\.[0-9]{2})', text)
                        if price_match:
                            potential_price = float(price_match.group(1))
                            if 40 < potential_price < 200:
                                price_data = potential_price
                                break
                    if price_data:
                        break
            
            # If we found price data, look for change data
            if price_data:
                # Look for change patterns
                change_patterns = re.findall(r'([+-][0-9]+\.[0-9]+)', page_text)
                if change_patterns:
                    try:
                        change_data = float(change_patterns[0])
                    except (ValueError, IndexError):
                        pass
                
                # Look for percentage patterns
                percent_patterns = re.findall(r'([+-]?[0-9]+\.[0-9]+)%', page_text)
                if percent_patterns:
                    try:
                        change_percent = float(percent_patterns[0])
                    except (ValueError, IndexError):
                        pass
            
            if not price_data:
                return None
            
            # Convert price from US cents to AUD$/bale
            exchange_rate = get_usd_to_aud()
            if exchange_rate is None:
                return None
            
            # Cotton futures are in US cents per pound, convert to AUD$/bale
            price_aud = round(((price_data * exchange_rate) / 100) * 500, 2)
            
            # Use percentage change if available, otherwise calculate from raw change
            if change_percent is not None:
                final_change = change_percent
            elif change_data is not None:
                previous_price = price_data - change_data
                if previous_price != 0:
                    final_change = round((change_data / previous_price) * 100, 2)
                else:
                    final_change = 0.0
            else:
                final_change = 0.0
            
            return {
                "commodity": f"Cotton ({contract_name})",
                "price": price_aud,
                "currency": "AUD",
                "change": final_change,
                "unit": "$/bale",
                "source": url,
                "timestamp": datetime.now(),
            }
            
        except Exception:
            return None
    
    # Scrape all contracts
    results = []
    for contract_name, url in contracts_to_scrape:
        contract_data = scrape_single_contract(contract_name, url)
        if contract_data:
            results.append(contract_data)
    
    if not results:
        raise ValueError("Could not extract any cotton futures prices from Barchart")
    
    # Return the first successful contract for backward compatibility
    # (the app expects a single dict, not a list)
    return results[0]

def scrape_cotton_futures_all():
    """
    Scrape all 5 cotton futures contracts including cash from Barchart.
    Returns a list of all contract data.
    """
    from datetime import datetime as dt
    
    # Cotton futures trade with contract months: March (H), May (K), July (N), October (V), December (Z)
    current_month = dt.now().month
    current_year = dt.now().year % 100  # Get last 2 digits of year
    current_full_year = dt.now().year
    
    # Define the contract month codes and their corresponding months
    contract_months = [
        (3, "H"),   # March
        (5, "K"),   # May
        (7, "N"),   # July
        (10, "V"),  # October
        (12, "Z")   # December
    ]
    
    # Build list of 5 most recent contracts including cash
    contracts_to_scrape = []
    
    # Add cash/spot contract - this will show as CTY00 (Cash)
    contracts_to_scrape.append(("Cotton Cash", "https://www.barchart.com/futures/quotes/cotton"))
    
    # Generate the next 4-5 active contract months starting from current/next active month
    all_possible_contracts = []
    
    # Build list of all possible contracts for the next 18 months
    for year_offset in range(3):  # Check current year and next 2 years
        check_year = (current_year + year_offset) % 100
        check_full_year = current_full_year + year_offset
        
        for month_num, month_code in contract_months:
            # For current year, only add contracts that haven't expired (or are in current month)
            if year_offset == 0 and month_num < current_month:
                continue
            
            # Create contract date for sorting
            contract_date = dt(check_full_year, month_num, 1)
            
            all_possible_contracts.append({
                'symbol': f"CT{month_code}{check_year:02d}",
                'name': f"Cotton {month_code}{check_year:02d}",
                'url': f"https://www.barchart.com/futures/quotes/CT{month_code}{check_year:02d}",
                'date': contract_date,
                'month_code': month_code,
                'year': check_year
            })
    
    # Sort by date to get the most current contracts first
    all_possible_contracts.sort(key=lambda x: x['date'])
    
    # Take the first 4 contracts (most immediate/liquid)
    for contract in all_possible_contracts[:4]:
        contracts_to_scrape.append((contract['name'], contract['url']))
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    def scrape_single_contract(contract_name, url):
        """Scrape a single cotton contract"""
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text()
            
            price_data = None
            change_data = None
            change_percent = None
            
            # Method 1: Look for "Last Price" pattern in text
            last_price_match = re.search(r'Last Price[:\s]*([0-9]+\.?[0-9]*)', page_text, re.IGNORECASE)
            if last_price_match:
                potential_price = float(last_price_match.group(1))
                if 40 < potential_price < 200:  # Reasonable cotton price range in cents
                    price_data = potential_price
            
            # Method 2: Look for price patterns in the text content
            if not price_data:
                price_patterns = re.findall(r'([0-9]{2,3}\.[0-9]{1,2})[s]?', page_text)
                for price_str in price_patterns:
                    potential_price = float(price_str)
                    if 40 < potential_price < 200:
                        price_data = potential_price
                        break
            
            # Method 3: Look in specific HTML elements
            if not price_data:
                for tag in ['span', 'div', 'td']:
                    elements = soup.find_all(tag, string=re.compile(r'[0-9]{2,3}\.[0-9]{2}'))
                    for elem in elements:
                        text = elem.get_text(strip=True)
                        price_match = re.search(r'([0-9]{2,3}\.[0-9]{2})', text)
                        if price_match:
                            potential_price = float(price_match.group(1))
                            if 40 < potential_price < 200:
                                price_data = potential_price
                                break
                    if price_data:
                        break
            
            # If we found price data, look for change data
            if price_data:
                # Look for change patterns
                change_patterns = re.findall(r'([+-][0-9]+\.[0-9]+)', page_text)
                if change_patterns:
                    try:
                        change_data = float(change_patterns[0])
                    except (ValueError, IndexError):
                        pass
                
                # Look for percentage patterns
                percent_patterns = re.findall(r'([+-]?[0-9]+\.[0-9]+)%', page_text)
                if percent_patterns:
                    try:
                        change_percent = float(percent_patterns[0])
                    except (ValueError, IndexError):
                        pass
            
            if not price_data:
                return None
            
            # Convert price from US cents to AUD$/bale
            exchange_rate = get_usd_to_aud()
            if exchange_rate is None:
                return None
            
            # Cotton futures are in US cents per pound, convert to AUD$/bale
            price_aud = round(((price_data * exchange_rate) / 100) * 500, 2)
            
            # Use percentage change if available, otherwise calculate from raw change
            if change_percent is not None:
                final_change = change_percent
            elif change_data is not None:
                previous_price = price_data - change_data
                if previous_price != 0:
                    final_change = round((change_data / previous_price) * 100, 2)
                else:
                    final_change = 0.0
            else:
                final_change = 0.0
            
            return {
                "commodity": f"Cotton ({contract_name})",
                "price": price_aud,
                "currency": "AUD",
                "change": final_change,
                "unit": "$/bale",
                "source": url,
                "timestamp": datetime.now(),
            }
            
        except Exception:
            return None
    
    # Scrape all contracts
    results = []
    for contract_name, url in contracts_to_scrape:
        contract_data = scrape_single_contract(contract_name, url)
        if contract_data:
            results.append(contract_data)
    
    if not results:
        raise ValueError("Could not extract any cotton futures prices from Barchart")
    
    # Return all contracts
    return results

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
    price = float(row.find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").text)
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
