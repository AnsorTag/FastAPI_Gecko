from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.sql import func
from app.databases.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    crypto_name = Column(String, index=True)
    amount = Column(Float)
    price_usd = Column(Float)
    timestamp = Column(TIMESTAMP, server_default=func.now())
