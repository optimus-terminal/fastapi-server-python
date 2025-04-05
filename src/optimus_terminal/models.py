from typing import List, Optional

from pydantic import BaseModel


# Inputs for Stock News APIs
class StockRequestData(BaseModel):
    symbol: str  # Symbol of the Stock
    order: Optional[str] = "asc"  # Order: asc/desc
    limit: Optional[str] = "5"  # Limit: E.g. 10


class StockRequestLangChain(BaseModel):
    symbol: str  # Symbol of the Stock


# Outputs for Stock Price API
class StockEntry(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockResponse(BaseModel):
    symbol: str
    entries: List[StockEntry]


class WatchListElement(BaseModel):
    ticker: str
    last: float
    change: float
    changePer: float
    volume: float
    avgVolume: float
    marketCapacity: float
