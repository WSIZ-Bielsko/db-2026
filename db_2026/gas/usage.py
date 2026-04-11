import asyncio
import os
import random
from datetime import datetime
from random import choice

from dotenv import load_dotenv

from db_2026.gas.model import FuelType, FuelOffer
from db_2026.gas.pool import create_db_pool
from db_2026.gas.repo import FuelRepository


async def insert_random_price(repo: FuelRepository):
    types = await repo.get_fuel_types()
    stations = await repo.get_gas_stations()

    t_ids = [t.id for t in types]
    s_ids = [s.id for s in stations]

    new_price = FuelOffer(station_id=choice(s_ids), fuel_type_id=choice(t_ids),
                          posted_at=datetime.now(),
                          price_per_liter=round(random.uniform(5.0, 10.0), 2))
    await repo.create_fuel_offer(new_price)

async def main():
    load_dotenv()
    db_url = os.getenv("DB_URL")
    pool = await create_db_pool(db_url)

    # Pass the pool to your repository
    repo = FuelRepository(pool)

    # ft = FuelType(name="Diesel Premium")
    # x = await repo.create_fuel_type(ft)
    # print(x)

    await insert_random_price(repo)



    # Don't forget to close the pool when shutting down
    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())