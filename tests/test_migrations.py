from pathlib import Path

import pytest

from future.database import Database
from future.databases.SQLiteDatabase import SQLiteDatabase
from future.interfaces.IModel import IModel
from future.migrations import Migrator, MigrationGenerator, Schema


class Widget(IModel):
    __connection__ = "default"
    __table__ = "widgets"
    id: str
    name: str


def _sqlite():
    Database._connections = {}
    Database._default = None
    Database().set_connection_details({"default": "sqlite", "sqlite": SQLiteDatabase(database=":memory:")})
    return Database().get_connection("default")


async def test_schema_create_and_drop_roundtrip():
    connection = _sqlite()
    Schema.connection("default")
    async with Schema.create("widgets") as table:
        table.id()
        table.string("name")
        table.integer("count").nullable()
        table.timestamps()
    assert await connection.table_exists("widgets") is True
    await Widget(id="1", name="w").save()
    found = await Widget.find("1")
    assert found is not None and found.name == "w"
    await Schema.drop("widgets")
    assert await connection.table_exists("widgets") is False
    await connection.disconnect()


async def test_model_raises_when_table_missing():
    connection = _sqlite()
    with pytest.raises(RuntimeError, match="does not exist"):
        await Widget.find("1")
    await connection.disconnect()


async def test_migrator_run_is_idempotent_then_rollback(tmp_path):
    connection = _sqlite()
    mig_dir = tmp_path / "migrations"
    mig_dir.mkdir()
    (mig_dir / "2026_01_01_create_widgets.py").write_text(
        "from future.migrations import Migration, Schema\n"
        "\n"
        "\n"
        "class CreateWidgets(Migration):\n"
        '    __connection__ = "default"\n'
        "\n"
        "    async def up(self):\n"
        '        async with Schema.create("widgets") as table:\n'
        "            table.id()\n"
        '            table.string("name")\n'
        "\n"
        "    async def down(self):\n"
        '        await Schema.drop("widgets")\n'
    )
    migrator = Migrator(path=str(mig_dir))
    assert await migrator.run() == ["2026_01_01_create_widgets"]
    assert await migrator.run() == []
    assert await connection.table_exists("widgets") is True
    assert await migrator.rollback() == ["2026_01_01_create_widgets"]
    assert await connection.table_exists("widgets") is False
    await connection.disconnect()


def test_migration_generator_skips_imodel_relations(tmp_path):
    framework_root = Path(__file__).resolve().parents[1]
    gen = MigrationGenerator(models_path=str(framework_root / "future" / "models"), migrations_path=str(tmp_path))
    paths = gen.make("PostModel")
    text = Path(paths[0]).read_text()
    assert "async def up" in text
    assert "async with Schema.create" in text
    assert 'table.string("title")' in text
    assert 'table.string("author_id")' in text
    assert 'table.string("author")' not in text
