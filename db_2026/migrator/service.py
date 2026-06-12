from asyncio import run
from os import environ
from typing import Any

import asyncpg
from asyncpg import UndefinedTableError
from dotenv import load_dotenv
from loguru import logger

from db_2026.migrator.model import Version, Migration, plan_migrations, MigrationError


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

    async def migrate(self, migration: Migration, direction: str):
        m = migration # alias
        current_version = await self.current_db_version()
        logger.info(f'running migration: {m.name}, id: {m.id}, direction: {direction}')

        if direction == 'UP':
            if current_version.version != m.prev_id:
                raise MigrationError(f"Migration {m.id} is not valid. "
                                     f"Current version is {current_version.version}, migration requires {m.prev_id}")
            await self.__execute_sql(m.up_script)
            logger.info(f"Migration {m.id} applied ({direction})")
            await self.__execute_sql(f"UPDATE version SET version = '{m.id}', level = {m.level}",)
            logger.debug(f"Version updated to {m.id}")
        elif direction == 'DOWN':
            if current_version.version != m.id:
                raise MigrationError(f"Migration {m.id} is not valid. "
                                     f"Current version is {current_version.version}, migration requires {m.id}")
            await self.__execute_sql(m.down_script)
            logger.info(f"Migration {m.id} applied ({direction})")
            await self.__execute_sql(f"UPDATE version SET version = '{m.prev_id}', level = {m.level-1}",)
            logger.debug(f"Version updated to {m.prev_id}")
        else:
            raise MigrationError(f"Invalid direction: {direction}")


async def main():
    load_dotenv()
    db_url = environ["DB_URL"]
    migration_dir = 'db'
    service = MigratorService(db_url, migration_dir=migration_dir)
    await service.connect()
    ver = await service.current_db_version()
    logger.info(f"Current database version: {ver}")

    plan = plan_migrations(path=migration_dir, last_executed_migration_id='START', target_migration='M3')


    for m in plan.migrations:
        await service.migrate(m, direction=plan.direction)

    await service.shutdown()


if __name__ == '__main__':
    run(main())
