import os

import asyncpg
from dotenv import load_dotenv


async def create_db_pool() -> asyncpg.Pool:
    load_dotenv()
    db_url = os.getenv("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable is not set")
    return await asyncpg.create_pool(dsn=db_url)