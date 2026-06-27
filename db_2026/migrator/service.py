from asyncio import run
from os import environ
from typing import Any

from dotenv import load_dotenv
from loguru import logger

from db_2026.migrator import executor
from db_2026.migrator.executor import QueryExecutor, PostgresQueryExecutor
from db_2026.migrator.model import Version, Migration, MigrationError, get_migration_by_id, get_migration_list, \
    plan_migrations


class MigratorService:

    def __init__(self, migration_dir: str, executor: QueryExecutor):
        self.migration_dir = migration_dir
        self.executor = executor


    async def __execute_script(self, script: str) -> Any:
        return await self.executor.execute_script(script)

    async def current_db_version(self) -> Version:
        return await self.executor.get_version()

    async def migrate(self, migration: Migration, direction: str):
        m = migration # alias
        current_version = await self.current_db_version()
        logger.info(f'running migration: {m.name}, id: {m.id}, direction: {direction}')

        if direction == 'UP':
            if current_version.version != m.prev_id:
                raise MigrationError(f"Migration {m.id} is not valid. "
                                     f"Current version is {current_version.version}, migration requires {m.prev_id}")
            await self.__execute_script(m.up_script)
            logger.info(f"Migration {m.id} applied ({direction})")

            await self.executor.update_version(Version(version=m.id, level=m.level))

            logger.debug(f"Version updated to {m.id}")
        elif direction == 'DOWN':
            if current_version.version != m.id:
                raise MigrationError(f"Migration {m.id} is not valid. "
                                     f"Current version is {current_version.version}, migration requires {m.id}")
            await self.__execute_script(m.down_script)
            logger.info(f"Migration {m.id} applied ({direction})")
            await self.executor.update_version(Version(version=m.prev_id, level=m.level-1))
            logger.debug(f"Version updated to {m.prev_id}")
        else:
            raise MigrationError(f"Invalid direction: {direction}")

    async def rollback_last(self):
        current_version = await self.current_db_version()
        if current_version.version == 'START':
            logger.warning("Cannot rollback from START version")
            return
        last_migration = get_migration_by_id(path=self.migration_dir, id=current_version.version)
        if not last_migration:
            raise MigrationError(f"Migration {current_version.version} not found")
        await self.migrate(last_migration, direction='DOWN')
        logger.info(f"Rolled back last migration: {current_version.version}")

    async def upgrade_head(self):
        """
        Executes all necessary migrations to bring DB to the highest level (as defined by files in self.migration_dir).
        :return:
        """


        current_version = await self.current_db_version()
        last_migration = get_migration_list(self.migration_dir)[-1]

        plan = plan_migrations(path=self.migration_dir,
                               last_executed_migration_id=current_version.version,
                               target_migration=last_migration.id)
        logger.info(f'executing all migrations up to head: {last_migration.id} / {last_migration.level} /{last_migration.name}')
        for m in plan.migrations:
            await self.migrate(m, direction=plan.direction)




async def main():
    load_dotenv()

    db_url = environ["DB_URL"]
    dir = environ["MIGRATION_DIR"]

    executor = PostgresQueryExecutor(db_url=db_url)

    await executor.initialize()
    # logger.debug(f'version: {await cass_executor.get_version()}')
    # await cass_executor.update_version(Version(version='START', level=0))
    # logger.debug(f'version: {await cass_executor.get_version()}')
    # sleep(1)


    service = MigratorService(executor=executor, migration_dir=dir)
    # await service.connect()
    # ver = await service.current_db_version()
    # logger.info(f"Current database version: {ver}")

    # MIGRATE SELECTIVCE
    # plan = plan_migrations(path=migration_dir, last_executed_migration_id='START', target_migration='M3')
    #
    # for m in plan.migrations:
    #     await service.migrate(m, direction=plan.direction)

    # await service.rollback_last()
    await service.rollback_last()
    await service.rollback_last()

    await service.upgrade_head()
    await executor.shutdown()



if __name__ == '__main__':
    run(main())
