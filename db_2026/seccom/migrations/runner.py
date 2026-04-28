import asyncio
import os
import asyncpg
from dotenv import load_dotenv

# migrations to run - in order
TIME_LINE = [0,1,2,3,4,5]

async def run_migration():
    load_dotenv()
    #todo: write the eingine to execute the migrations
    sql = open("migration.sql", "r").read()
    conn = await asyncpg.connect(os.getenv("DATABASE_URL")) # specify it in .env file locally here
    await conn.execute(sql)
    await conn.close()

asyncio.run(run_migration())