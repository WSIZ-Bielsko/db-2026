import asyncio
import os
from asyncio import create_task
from datetime import datetime
from decimal import Decimal
from random import uniform, choice

from dotenv import load_dotenv
from loguru import logger

from db_2026.gas.model import GasStation, FuelOffer
from db_2026.gas.pool import create_db_pool
from db_2026.gas.repo import FuelRepository

def ts():
    return datetime.now().timestamp()

async def create_random_offers(repo: FuelRepository, fuel_type_id: int):
    stations = await repo.get_gas_stations()
    s_ids = [s.id for s in stations]
    st = ts()

    n_offers = 1000
    t = []
    for _ in range(n_offers):
        offer = FuelOffer(price_per_liter=Decimal(str(round(uniform(5.0, 10.0), 1))),
                          station_id=choice(s_ids),posted_at=datetime.now(),
                          fuel_type_id=fuel_type_id)
        t.append(create_task(repo.create_fuel_offer(offer)))
    await asyncio.gather(*t)
    en = ts()
    logger.info(f"Created {n_offers} offers for fuel type {fuel_type_id} in {en-st:.3f} seconds")



async def main():
    load_dotenv()
    db_url = os.getenv("DB_URL")
    pool = await create_db_pool(db_url)
    repo = FuelRepository(pool)


    await create_random_offers(repo, 1)


    await pool.close()





if __name__ == "__main__":
    asyncio.run(main())