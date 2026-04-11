import asyncpg

async def create_db_pool(db_url: str) -> asyncpg.Pool:
    return await asyncpg.create_pool(dsn=db_url)