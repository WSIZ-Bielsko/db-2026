import os

from pydantic import BaseModel
from loguru import logger


class Migration(BaseModel):
    name: str
    up_script: str
    down_script: str
    level: int
    # id's below are ~6 letter strings
    id: str
    prev_id: str
    next_id: str


class Version(BaseModel):
    version: str
    level: int

def save_migration(path: str, filename: str, migration: Migration):
    full_path = os.path.join(path, filename)
    logger.info(f"Saving migration {migration.id} to {full_path}")
    with open(full_path, 'w') as f:
        f.write(migration.model_dump_json(indent=2))
    logger.info(f"Migration {migration.id} saved")


def load_migration(path: str, filename: str) -> Migration:
    full_path = os.path.join(path, filename)
    with open(full_path, 'r') as f:
        return Migration.model_validate_json(f.read())


def get_migration_list(path: str) -> list[Migration]:
    """
    Return a list of migrations sorted by level
    :param path:
    :return:
    """
    return sorted(
        [load_migration(path, f) for f in os.listdir(path) if f.startswith('m') and f.endswith(".json")],
        key=lambda m: m.level
    )


def get_migration_by_id(path: str, id: str) -> Migration | None:
    for m in get_migration_list(path):
        if m.id == id:
            return m
    return None


def plan_migrations(path: str, last_executed_migration_id: str,
                    target_migration: str | None) -> list[Migration]:
    """
    For "UP" migrations (M1,M3): ["M1", "M2", "M3"] will be returned.
    For "DOWN" migrations: (M3, M1): ["M3", "M2", "M1"] will be returned.

    :param path:
    :param last_executed_migration_id:
    :param target_migration:
    :param target_level:
    :return:
    """
    m_src = get_migration_by_id(path, last_executed_migration_id)
    m_tgt = get_migration_by_id(path, target_migration)
    mm = get_migration_list(path)
    src_idx = mm.index(m_src)
    tgt_idx = mm.index(m_tgt)

    logger.info(f"src_idx={src_idx}, tgt_idx={tgt_idx}")

    if m_tgt.level > m_src.level:
        direction = 'UP'
        logger.info(f"direction={direction}")
        return mm[src_idx + 1: tgt_idx + 1]
    else:
        direction = 'DOWN'
        return mm[tgt_idx+1: src_idx + 1][::-1]


if __name__ == '__main__':
    # test_save_load_migration()
    mm = get_migration_list("db")
    print(mm)
    for m in mm:
        print(m.model_dump())
    # print('----' * 5)
    # m2 = get_migration_by_id("db", "123457")
    #
    # idx = mm.index(m2)
    # print(f"idx={idx}")
    # print(mm[idx])

    print('----' * 5)
    for m in plan_migrations("123456", "123458", target_level=None):
        print(m.model_dump())

    print('----' * 5)
    for m in plan_migrations("123458", "123456", target_level=None):
        print(m.model_dump())

