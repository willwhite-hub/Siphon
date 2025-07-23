import requests

def get_usd_to_aud():
    """
    Fetch the current exchange rate from USD to AUD.
    Returns:
        float: The exchange rate from USD to AUD.
    """
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    try:
        # Make a GET request to the exchange rate API
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        return data['rates']['AUD']  # Return the AUD rate from the response
    except requests.RequestException as e:
        print(f"Error fetching exchange rate: {e}")
        return None
        