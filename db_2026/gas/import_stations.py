import asyncio
import os
from decimal import Decimal

from dotenv import load_dotenv

from db_2026.gas.model import GasStation
from db_2026.gas.pool import create_db_pool
from db_2026.gas.repo import FuelRepository





def import_stations(repo: FuelRepository, stations: list[GasStation]):
    for station in stations:
        repo.create_gas_station(station)

async def main():
    load_dotenv()
    db_url = os.getenv("DB_URL")
    pool = await create_db_pool(db_url)
    repo = FuelRepository(pool)

    gas_stations = [
        # Kraków
        GasStation(
            name="Shell Wielicka",
            city="Kraków",
            address="ul. Wielicka 77, 30-552 Kraków",
            x=Decimal("50.033100"),
            y=Decimal("19.974200"),
        ),
        GasStation(
            name="Shell Zakopiańska",
            city="Kraków",
            address="ul. Zakopiańska 48, 30-418 Kraków",
            x=Decimal("50.017800"),
            y=Decimal("19.913500"),
        ),
        GasStation(
            name="Shell Conrada",
            city="Kraków",
            address="ul. Conrada 36, 31-357 Kraków",
            x=Decimal("50.096200"),
            y=Decimal("19.900400"),
        ),
        GasStation(
            name="Orlen Aleja Pokoju",
            city="Kraków",
            address="al. Pokoju 3, 31-548 Kraków",
            x=Decimal("50.065300"),
            y=Decimal("20.005700"),
        ),
        GasStation(
            name="BP Opolska",
            city="Kraków",
            address="ul. Opolska 60, 31-277 Kraków",
            x=Decimal("50.083400"),
            y=Decimal("19.951600"),
        ),
        # Warsaw
        GasStation(
            name="Orlen Aleja 3 Maja",
            city="Warszawa",
            address="al. 3 Maja 1A, 00-401 Warszawa",
            x=Decimal("52.229700"),
            y=Decimal("21.012200"),
        ),
        GasStation(
            name="Orlen Grzybowska",
            city="Warszawa",
            address="ul. Grzybowska 74, 00-844 Warszawa",
            x=Decimal("52.234500"),
            y=Decimal("20.990100"),
        ),
        GasStation(
            name="Shell Karolkowa",
            city="Warszawa",
            address="ul. Karolkowa 30, 01-207 Warszawa",
            x=Decimal("52.234900"),
            y=Decimal("20.975300"),
        ),
        GasStation(
            name="BP Grochowska",
            city="Warszawa",
            address="ul. Grochowska 149/151, 04-357 Warszawa",
            x=Decimal("52.244600"),
            y=Decimal("21.072800"),
        ),
        GasStation(
            name="Circle K Puławska",
            city="Warszawa",
            address="ul. Puławska 11, 02-515 Warszawa",
            x=Decimal("52.194300"),
            y=Decimal("21.019400"),
        ),
    ]

    await pool.close()





if __name__ == "__main__":
    asyncio.run(main())