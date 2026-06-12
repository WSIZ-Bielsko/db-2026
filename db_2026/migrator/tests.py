from db_2026.migrator.model import Migration, save_migration, load_migration




def test_zero():
    import os
    print(os.getcwd())

def test_save_load_migration():
    migration = Migration(name="test", up_script="up", down_script="down", level=1, id="123457", prev_id="12345",
                          next_id="1234567")
    path = "tests/migrator/db"
    save_migration(path=path, filename="m_002_.json", migration=migration)
    loaded_migration = load_migration(path, "m_002_.json")
    assert migration.model_dump() == loaded_migration.model_dump()
