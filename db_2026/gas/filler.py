from faker import Faker
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from db_2026.gas.model import FuelOffer

fake = Faker()

station_id = uuid4()

fuel_offers = [
    FuelOffer(
        price_per_liter=Decimal(round(fake.pyfloat(min_value=1.0, max_value=3.0, right_digits=2), 2)),
        station_id=station_id,
        posted_at=fake.date_time_this_year(),
        fuel_type_id=fake.random_int(min=1, max=5)
    )
    for _ in range(10)
]