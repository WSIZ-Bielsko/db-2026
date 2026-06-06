import os

from pydantic import BaseModel


class Migration(BaseModel):
    name: str
    up_script: str
    down_script: str
    level: int
    # id's below are ~6 letter strings
    id: str
    prev_id: str
    next_id: str



def save_migration(path: str, filename: str, migration: Migration):
    full_path = os.path.join(path, filename)
    with open(full_path, 'w') as f:
        f.write(migration.model_dump_json(indent=2))


def load_migration(path: str, filename: str) -> Migration:
    full_path = os.path.join(path, filename)
    with open(full_path, 'r') as f:
        return Migration.model_validate_json(f.read())


"""
level 1: id=aabbcc
level 2: id=aabbdc
level 3: id=ddccag


on the DB -- table "versioning"
- current_level
- last_migration_id
- db_name

"""

def test_save_load_migration():
    migration = Migration(name="test", up_script="up", down_script="down", level=1, id="123457", prev_id="12345", next_id="1234567")
    save_migration("db", "m_002.json", migration)
    loaded_migration = load_migration("db", "m_002.json")
    assert migration.model_dump() == loaded_migration.model_dump()



def get_migration_list(path: str) -> list[Migration]:
    return sorted(
        [load_migration(path, f) for f in os.listdir(path) if f.startswith('m') and f.endswith(".json")],
        key=lambda m: m.level
    )

if __name__ == '__main__':
    test_save_load_migration()
    for m in get_migration_list("db"):
        print(m.model_dump())