from datetime import datetime

from future.database import Database
from future.databases.SQLiteDatabase import SQLiteDatabase
from future.migrations import Blueprint
from future.interfaces.IModel import IModel


class Item(IModel):
    __connection__ = "sqlite"
    __table__ = "items"

    id: str
    name: str
    price: float
    active: bool


def _register(database=":memory:"):
    Database().set_connection_details({
        "default": "sqlite",
        "sqlite": SQLiteDatabase(database=database),
    })
    return Database().get_connection("sqlite")


async def _create_items_table(connection):
    blueprint = Blueprint("items", "sqlite", action="create")
    blueprint.id()
    blueprint.string("name")
    blueprint.float("price")
    blueprint.boolean("active")
    blueprint.timestamps()
    await connection.schema_create(blueprint)


async def test_sqlite_connect_memory():
    connection = _register(":memory:")
    assert await connection.connect() is not None
    await connection.disconnect()


async def test_sqlite_connect_creates_file(tmp_path):
    name = str(tmp_path / "app")
    connection = _register(name)
    await connection.connect()
    assert (tmp_path / "app.sqlite").exists()
    await connection.disconnect()


async def test_sqlite_schema_and_crud():
    connection = _register(":memory:")
    await _create_items_table(connection)

    item = Item(id="1", name="apple", price=1.5, active=True, created_at=datetime(2026, 1, 1), updated_at=datetime(2026, 1, 1))
    await item.save()

    found = await Item.find("1")
    assert found is not None
    assert found.name == "apple"
    assert float(found.price) == 1.5
    assert int(found.active) == 1

    await item.update(name="pear", price=2.0)
    found = await Item.find("1")
    assert found.name == "pear"
    assert float(found.price) == 2.0

    await Item(id="2", name="banana", price=0.5, active=False).save()
    all_items = await Item.all()
    assert len(all_items) == 2

    cheap = await Item.where("price", "<", 1.0).get()
    assert len(cheap) == 1
    assert cheap[0].name == "banana"

    like_rows = await Item.where("name", "like", "%anana").get()
    assert len(like_rows) == 1
    assert like_rows[0].name == "banana"

    ordered = await Item.order_by("price", "desc").get()
    assert ordered[0].name == "pear"

    await (await Item.find("2")).delete()
    assert await Item.find("2") is None
    assert len(await Item.all()) == 1

    await connection.schema_drop("items")
    await connection.disconnect()


async def test_sqlite_upsert_on_save():
    connection = _register(":memory:")
    await _create_items_table(connection)

    await Item(id="1", name="a", price=1.0, active=True).save()
    await Item(id="1", name="b", price=3.0, active=False).save()
    found = await Item.find("1")
    assert found.name == "b"
    assert float(found.price) == 3.0
    assert len(await Item.all()) == 1
    await connection.disconnect()


async def test_sqlite_migrations_table():
    connection = _register(":memory:")
    assert await connection.migrations_get() == []
    assert await connection.migrations_max_batch() == 0

    await connection.migrations_put("2026_01_01_create_items", 1)
    await connection.migrations_put("2026_01_02_create_orders", 1)
    await connection.migrations_put("2026_01_03_alter_items", 2)

    assert await connection.migrations_get() == ["2026_01_01_create_items", "2026_01_02_create_orders", "2026_01_03_alter_items"]
    assert await connection.migrations_max_batch() == 2
    assert await connection.migrations_batch_for("2026_01_02_create_orders") == 1
    assert await connection.migrations_batch_for("missing") is None

    await connection.migrations_delete("2026_01_03_alter_items")
    assert await connection.migrations_get() == ["2026_01_01_create_items", "2026_01_02_create_orders"]
    assert await connection.migrations_max_batch() == 1
    await connection.disconnect()


async def test_sqlite_file_persists_across_connections(tmp_path):
    name = str(tmp_path / "persist")
    connection = _register(name)
    await _create_items_table(connection)
    await Item(id="1", name="kept", price=9.0, active=True).save()
    await connection.disconnect()

    connection = _register(name)
    found = await Item.find("1")
    assert found is not None
    assert found.name == "kept"
    await connection.disconnect()


async def test_sqlite_where_in_and_not_equal():
    connection = _register(":memory:")
    await _create_items_table(connection)
    await Item(id="1", name="apple", price=1.0, active=True).save()
    await Item(id="2", name="pear", price=2.0, active=True).save()
    await Item(id="3", name="banana", price=3.0, active=False).save()
    rows = await Item.where("id", "in", ["1", "3"]).order_by("price", "asc").get()
    assert [row.name for row in rows] == ["apple", "banana"]
    rows = await Item.where("name", "!=", "pear").get()
    assert {row.name for row in rows} == {"apple", "banana"}
    empty = await Item.where("id", "in", []).get()
    assert empty == []
    await connection.disconnect()


async def test_sqlite_schema_via_async_with():
    from future.migrations import Schema
    connection = _register(":memory:")
    Schema.connection("sqlite")
    async with Schema.create("items") as table:
        table.id()
        table.string("name")
        table.float("price")
        table.boolean("active")
        table.timestamps()
    await Item(id="1", name="via-schema", price=4.0, active=True).save()
    found = await Item.find("1")
    assert found.name == "via-schema"
    await connection.disconnect()
