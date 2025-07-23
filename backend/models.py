from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Price(Base):
    """
    Represents a commodity price record in the database.
    Attributes:
        id (int): Unique identifier for the price record.
        commodity (str): Name of the commodity.
        price (float): Price of the commodity.
        change (float): Change in price.
        unit (str): Unit of measurement for the price.
        timestamp (datetime): Timestamp when the price was recorded.
        source (str): Source URL for the price data.
    """
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String)
    price = Column(Float)
    currency = Column(String, default="AUD")  # Default currency is AUD
    change = Column(Float)
    unit = Column(String)
    timestamp = Column(DateTime)
    source = Column(String)

def __repr__(self):
        return (
            f"<Price(commodity={self.commodity}, price={self.price}, "
            f"change={self.change}, unit={self.unit}, "
            f"timestamp={self.timestamp}, source={self.source})>"
        )