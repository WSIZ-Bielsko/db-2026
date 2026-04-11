from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

class FuelType(BaseModel):
    id: int | None = None
    name: str

class GasStation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    city: str
    address: str
    x: Decimal = Field(max_digits=8, decimal_places=6)
    y: Decimal = Field(max_digits=9, decimal_places=6)

class FuelOffer(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    price_per_liter: Decimal = Field(max_digits=4, decimal_places=2)
    station_id: UUID
    posted_at: datetime
    fuel_type_id: int

