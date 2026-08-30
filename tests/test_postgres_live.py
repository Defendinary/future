import pytest

from future.database import Database
from future.databases.PostgresDatabase import PostgresDatabase
from future.migrations import Schema
from future.interfaces.IModel import IModel


def _postgres_ready() -> bool:
    import socket
    try:
        sock = socket.create_connection(("127.0.0.1", 5432), timeout=0.5)
        sock.close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _postgres_ready(), reason="Postgres st0nkz not reachable at 127.0.0.1:5432")


class Widget(IModel):
    __table__ = "widgets_test"
    __connection__ = "postgres"


async def test_postgres_schema_seed_and_query():
    postgres = PostgresDatabase(host="127.0.0.1", port=5432, username="postgres", password="postgres", database="st0nkz")
    Database().set_connection_details({"default": "postgres", "postgres": postgres})
    await postgres.schema_drop("widgets_test")
    Schema.connection("postgres")
    async with Schema.create("widgets_test") as table:
        table.id()
        table.string("name")
        table.float("price")

    await Widget(id="w1", name="alpha", price=10.5).save()
    await Widget(id="w2", name="beta", price=20.0).save()

    found = await Widget.find("w1")
    assert found is not None and found.name == "alpha"

    rows = await Widget.where("price", ">", 15).order_by("price", "desc").get()
    assert len(rows) == 1 and rows[0].id == "w2"

    await found.update(price=11.0)
    assert float((await Widget.find("w1")).price) == 11.0

    await found.delete()
    assert await Widget.find("w1") is None
    assert len(await Widget.all()) == 1

    await postgres.schema_drop("widgets_test")
