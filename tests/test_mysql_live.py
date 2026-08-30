import pytest

from future.database import Database
from future.databases.MySQLDatabase import MySQLDatabase
from future.migrations import Schema
from future.interfaces.IModel import IModel


def _mysql_ready() -> bool:
    import socket
    try:
        sock = socket.create_connection(("127.0.0.1", 3306), timeout=0.5)
        sock.close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _mysql_ready(), reason="MySQL st0nkz not reachable at 127.0.0.1:3306")


class Widget(IModel):
    __table__ = "widgets_test"
    __connection__ = "mysql"


async def test_mysql_schema_seed_and_query():
    mysql = MySQLDatabase(host="127.0.0.1", port=3306, username="root", password="password", database="st0nkz")
    Database().set_connection_details({"default": "mysql", "mysql": mysql})
    await mysql.schema_drop("widgets_test")
    Schema.connection("mysql")
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

    await mysql.schema_drop("widgets_test")
