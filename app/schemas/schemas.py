from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import Optional
from datetime import datetime


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
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("timestamp")
    def serialize_timestamp(self, timestamp: datetime, _info):
        return timestamp.isoformat()
