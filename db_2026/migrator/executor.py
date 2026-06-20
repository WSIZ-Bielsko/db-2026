from abc import ABC
from typing import Any

import asyncpg
from asyncpg import Pool, UndefinedTableError
from loguru import logger

from db_2026.migrator.model import Version


class QueryExecutor(ABC):

    async def initialize(self):
        """establish appropriate connections"""

    async def shutdown(self):
        """close connections"""

    async def execute_script(self, script: str) -> Any:
        """execute a script; return value if the script returns a value"""


    async def get_version(self) -> Version:
        """get the current version of the database"""


    async def update_version(self, version: Version):
        """update the current version of the database"""



class PostgresQueryExecutor(QueryExecutor):

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool: Pool = None


    async def initialize(self):
        logger.info("Connecting to database")
        self.pool = await asyncpg.create_pool(dsn=self.db_url)
        logger.info("Connected to database")

    async def shutdown(self):
        logger.info("Disconnecting from database")
        await self.pool.close()
        logger.info("Disconnected from database")

    async def execute_script(self, script: str) -> Any:
        async with self.pool.acquire() as conn:
            return await conn.fetch(script)

    async def get_version(self) -> Version:
        sql = "SELECT * FROM version"
        try:
            res = await self.execute_script(sql)
        except UndefinedTableError as e:
            await self.execute_script("CREATE TABLE version (version TEXT, level INTEGER)")
            await self.execute_script("INSERT INTO version (version, level) VALUES ('START', 0)")
            return Version(version="START", level=0)
        return Version(**(res[0]))

    async def update_version(self, version: Version):
        await self.execute_script(f"UPDATE version SET version = '{version.version}', level = {version.level}")