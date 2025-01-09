from pydantic import BaseModel, Field
from typing import Optional


class TransactionCreate(BaseModel):
    crypto_name: str = Field(..., title="Crypto Name", max_length=50)
    amount: float = Field(..., gt=0, title="Transaction Amount")
    price_usd: float = Field(..., title="Price in USD")


class TransactionUpdate(BaseModel):
    crypto_name: Optional[str] = Field(None, max_length=50)
    amount: Optional[float] = Field(None, gt=0)
    price_usd: Optional[float] = Field(None)


class TransactionResponse(BaseModel):
    id: int
    crypto_name: str
    amount: float
    price_usd: float
    timestamp: str

    class Config:
        orm_mode = True
