import asyncio
import os

from dotenv import load_dotenv

from db_2026.gas.model import FuelType
from db_2026.gas.pool import create_db_pool
from db_2026.gas.repo import FuelRepository


async def main():
    load_dotenv()
    db_url = os.getenv("DB_URL")
    pool = await create_db_pool(db_url)

    # Pass the pool to your repository
    repo = FuelRepository(pool)

    ft = FuelType(name="Diesel Premium")
    x = await repo.create_fuel_type(ft)
    print(x)

    # Don't forget to close the pool when shutting down
    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())