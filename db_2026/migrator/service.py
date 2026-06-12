from asyncio import run
from os import environ
from typing import Any

import asyncpg
from asyncpg import UndefinedTableError
from dotenv import load_dotenv
from loguru import logger

from db_2026.migrator.model import Version, Migration, plan_migrations


class MigrationError(Exception):
    pass

class MigratorService:

    def __init__(self, db_url: str, migration_dir: str):
        self.pool: asyncpg.Pool | None = None
        self.db_url = db_url
        self.migration_dir = migration_dir

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self.db_url)
        logger.info("Connected to database")

    async def shutdown(self):
        await self.pool.close()
        logger.info("Disconnected from database")

    async def __execute_sql(self, sql) -> Any:
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql)

    async def current_db_version(self) -> Version:
        sql = "SELECT * FROM version"
        try:
            res = await self.__execute_sql(sql)
        except UndefinedTableError as e:
            await self.__execute_sql("CREATE TABLE version (version TEXT, level INTEGER)")
            await self.__execute_sql("INSERT INTO version (version, level) VALUES ('START', 0)")
            return Version(version="START", level=0)
        return Version(**(res[0]))

    async def migrate(self, migration: Migration, direction='UP'):
        m = migration # alias
        current_version = await self.current_db_version()
        logger.info(f'running migration: {m.name}, id: {m.id}, direction: {direction}')
        if current_version.version != m.prev_id:
            raise MigrationError(f"Migration {m.id} is not valid. "
                                 f"Current version is {current_version.version}, migration requires {m.prev_id}")

        await self.__execute_sql(m.up_script)
        logger.info(f"Migration {m.id} applied")
        await self.__execute_sql(f"UPDATE version SET version = '{m.id}', level = {m.level}",)
        logger.debug(f"Version updated to {m.id}")




async def main():
    load_dotenv()
    db_url = environ["DB_URL"]
    service = MigratorService(db_url, migration_dir='db')
    await service.connect()
    ver = await service.current_db_version()
    logger.info(f"Current database version: {ver}")

    for m in plan_migrations(path='db', current_last_migration='M3', target_migration='M1', target_level=None):
        await service.migrate(m, direction='DOWN')

    await service.shutdown()


if __name__ == '__main__':
    run(main())
