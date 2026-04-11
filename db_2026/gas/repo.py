from uuid import UUID
import asyncpg
from db_2026.gas.model import FuelType, GasStation, FuelOffer

class FuelRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    # --- Fuel Type CRUD ---
    async def create_fuel_type(self, ft: FuelType) -> FuelType:
        query = "INSERT INTO fuel_type (name) VALUES ($1) RETURNING *"
        row = await self.pool.fetchrow(query, ft.name)
        return FuelType.model_validate(dict(row))

    async def get_fuel_type(self, id: int) -> FuelType | None:
        query = "SELECT * FROM fuel_type WHERE id = $1"
        row = await self.pool.fetchrow(query, id)
        return FuelType.model_validate(dict(row)) if row else None

    async def get_fuel_types(self) -> list[FuelType]:
        query = "SELECT * FROM fuel_type ORDER BY name"
        rows = await self.pool.fetch(query)
        return [FuelType.model_validate(dict(row)) for row in rows]

    async def update_fuel_type(self, id: int, ft: FuelType) -> FuelType | None:
        query = "UPDATE fuel_type SET name = $1 WHERE id = $2 RETURNING *"
        row = await self.pool.fetchrow(query, ft.name, id)
        return FuelType.model_validate(dict(row)) if row else None

    async def delete_fuel_type(self, id: int) -> bool:
        query = "DELETE FROM fuel_type WHERE id = $1"
        status = await self.pool.execute(query, id)
        return status != "DELETE 0"

    # --- Gas Station CRUD ---
    async def create_gas_station(self, gs: GasStation) -> GasStation:
        query = """
            INSERT INTO gas_station (id, name, city, address, x, y) 
            VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
        """
        row = await self.pool.fetchrow(
            query, gs.id, gs.name, gs.city, gs.address, gs.x, gs.y
        )
        return GasStation.model_validate(dict(row))

    async def get_gas_station(self, id: UUID) -> GasStation | None:
        query = "SELECT * FROM gas_station WHERE id = $1"
        row = await self.pool.fetchrow(query, id)
        return GasStation.model_validate(dict(row)) if row else None

    async def get_gas_stations(self) -> list[GasStation]:
        query = "SELECT * FROM gas_station ORDER BY name"
        rows = await self.pool.fetch(query)
        return [GasStation.model_validate(dict(row)) for row in rows]

    async def update_gas_station(self, id: UUID, gs: GasStation) -> GasStation | None:
        query = """
            UPDATE gas_station SET name = $1, city = $2, address = $3, x = $4, y = $5 
            WHERE id = $6 RETURNING *
        """
        row = await self.pool.fetchrow(
            query, gs.name, gs.city, gs.address, gs.x, gs.y, id
        )
        return GasStation.model_validate(dict(row)) if row else None

    async def delete_gas_station(self, id: UUID) -> bool:
        query = "DELETE FROM gas_station WHERE id = $1"
        status = await self.pool.execute(query, id)
        return status != "DELETE 0"

    # --- Fuel Offer CRUD ---
    async def create_fuel_offer(self, fo: FuelOffer) -> FuelOffer:
        query = """
            INSERT INTO fuel_offers (id, price_per_liter, station_id, posted_at, fuel_type_id) 
            VALUES ($1, $2, $3, $4, $5) RETURNING *
        """
        row = await self.pool.fetchrow(
            query, fo.id, fo.price_per_liter, fo.station_id, fo.posted_at, fo.fuel_type_id
        )
        return FuelOffer.model_validate(dict(row))

    async def get_fuel_offer(self, id: UUID) -> FuelOffer | None:
        query = "SELECT * FROM fuel_offers WHERE id = $1"
        row = await self.pool.fetchrow(query, id)
        return FuelOffer.model_validate(dict(row)) if row else None

    async def update_fuel_offer(self, id: UUID, fo: FuelOffer) -> FuelOffer | None:
        query = """
            UPDATE fuel_offers 
            SET price_per_liter = $1, station_id = $2, posted_at = $3, fuel_type_id = $4 
            WHERE id = $5 RETURNING *
        """
        row = await self.pool.fetchrow(
            query, fo.price_per_liter, fo.station_id, fo.posted_at, fo.fuel_type_id, id
        )
        return FuelOffer.model_validate(dict(row)) if row else None

    async def delete_fuel_offer(self, id: UUID) -> bool:
        query = "DELETE FROM fuel_offers WHERE id = $1"
        status = await self.pool.execute(query, id)
        return status != "DELETE 0"