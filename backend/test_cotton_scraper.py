#!/usr/bin/env python3
"""
Test script for the cotton futures scraper.
This script tests the scrape_cotton_futures() function to ensure it works correctly.
"""

from commodity_scraper import scrape_cotton_futures
import traceback

def test_cotton_futures():
    """Test the cotton futures scraper."""
    print("Testing Cotton Futures Scraper...")
    print("=" * 50)
    
    try:
        result = scrape_cotton_futures()
        
        # Validate the result structure
        required_keys = ['commodity', 'price', 'currency', 'change', 'unit', 'source', 'timestamp']
        missing_keys = [key for key in required_keys if key not in result]
        
        if missing_keys:
            print(f"ERROR: Missing keys in result: {missing_keys}")
            return False
        
        # Validate data types and ranges
        if not isinstance(result['price'], (int, float)) or result['price'] <= 0:
            print(f"ERROR: Invalid price: {result['price']}")
            return False
        
        if result['currency'] != 'AUD':
            print(f"ERROR: Expected currency AUD, got: {result['currency']}")
            return False
        
        if result['unit'] != '$/bale':
            print(f"ERROR: Expected unit $/bale, got: {result['unit']}")
            return False
        
        if not isinstance(result['change'], (int, float)):
            print(f"ERROR: Invalid change value: {result['change']}")
            return False
        
        # Print successful result
        print("SUCCESS: Cotton futures data scraped successfully!")
        print(f"Commodity: {result['commodity']}")
        print(f"Price: {result['price']} {result['currency']}")
        print(f"Change: {result['change']}%")
        print(f"Unit: {result['unit']}")
        print(f"Source: {result['source']}")
        print(f"Timestamp: {result['timestamp']}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cotton_futures()
    if success:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[FAILED] Tests failed!")
        exit(1)