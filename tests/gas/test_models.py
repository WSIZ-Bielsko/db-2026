from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from db_2026.gas.model import FuelType, GasStation, FuelOffer


# Assuming FuelType, GasStation, and FuelOffer are imported here

def test_fuel_type_valid():
    fuel = FuelType(name="95")
    assert fuel.name == "95"
    assert fuel.id is None

def test_fuel_type_missing_name():
    with pytest.raises(ValidationError):
        FuelType(id=1)  # Missing required 'name'

def test_gas_station_valid():
    station = GasStation(
        name="ORLEN",
        city="Bielsko-Biała",
        address="Al. Gen. Andersa 44",
        x=Decimal("19.040980"),
        y=Decimal("49.801219")
    )
    assert station.id is not None
    assert station.x == Decimal("19.040980")

def test_gas_station_invalid_x_digits():
    with pytest.raises(ValidationError):
        GasStation(
            name="ORLEN",
            city="Bielsko-Biała",
            address="Al. Gen. Andersa 44",
            x=Decimal("123.123456"),  # 9 digits total, exceeds max_digits=8
            y=Decimal("49.801219")
        )

def test_fuel_offer_valid():
    station_id = uuid4()
    offer = FuelOffer(
        price_per_liter=Decimal("6.09"),
        station_id=station_id,
        posted_at=datetime.now(),
        fuel_type_id=1
    )
    assert offer.price_per_liter == Decimal("6.09")
    assert offer.station_id == station_id

def test_fuel_offer_invalid_price():
    with pytest.raises(ValidationError):
        FuelOffer(
            price_per_liter=Decimal("123.45"),  # 5 digits total, exceeds max_digits=4
            station_id=uuid4(),
            posted_at=datetime.now(),
            fuel_type_id=1
        )