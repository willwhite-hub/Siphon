from sqlalchemy import create_engine    
from sqlalchemy.orm import sessionmaker
from models import Base, Price
from datetime import datetime

DB_FILE = "sqlite:///./data/prices.db"
engine =  create_engine(DB_FILE, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables if they don't exist
def init_db():
    Base.metadata.create_all(engine)

def insert_price(commodity, price, currency, change, unit, source, timestamp):
    """
    Insert a new price record into the database.
    Args:
        commodity (str): The name of the commodity.
        price (float): The price of the commodity.
        currency (str): The currency of the price.
        change (float): The change in price.
        unit (str): The unit of measurement for the price.
        source (str): The source URL for the price data.
        timestamp (datetime or str): The timestamp of the price data.
    """
    session = SessionLocal()
    try: 
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        new_price = Price(
            commodity=commodity,
            price=price,
            currency=currency,
            change=change,
            unit=unit,
            source=source,
            timestamp=timestamp
        )

        session.add(new_price)
        session.commit()
        print(f"Inserted price for {commodity} at {timestamp}.")

    except Exception as e:
        session.rollback()
        print(f"Error inserting price for {commodity}: {e}")
    finally:
        session.close()