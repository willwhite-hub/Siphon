from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CottonPrice(Base):
    __tablename__ = "cotton_prices"

    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String)
    price = Column(Float)
    change = Column(Float)
    published_at = Column(DateTime)
    source = Column(String)
