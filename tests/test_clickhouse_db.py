from unittest.mock import AsyncMock, MagicMock, patch

from future.databases.ClickhouseDatabase import ClickhouseDatabase
from future.interfaces.IModel import IModel


class Row(IModel):
    __table__ = "rows"


async def test_clickhouse_find():
    clickhouse = ClickhouseDatabase(host="localhost", port=9000, username="u", password="p", database="db")
    cursor = MagicMock()
    cursor.execute = AsyncMock()
    cursor.fetchall = AsyncMock(return_value=[("1", "n")])
    cursor.description = [("id",), ("name",)]
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=cursor)
    cm.__aexit__ = AsyncMock(return_value=None)
    clickhouse.client = MagicMock()
    clickhouse.client.cursor.return_value = cm
    found = await clickhouse.find(Row(), "1")
    assert found is not None and found.id == "1" and found.name == "n"


async def test_clickhouse_find_missing_returns_none():
    clickhouse = ClickhouseDatabase(host="localhost", port=9000, username="u", password="p", database="db")
    cursor = MagicMock()
    cursor.execute = AsyncMock()
    cursor.fetchall = AsyncMock(return_value=[])
    cursor.description = [("id",), ("name",)]
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=cursor)
    cm.__aexit__ = AsyncMock(return_value=None)
    clickhouse.client = MagicMock()
    clickhouse.client.cursor.return_value = cm
    assert await clickhouse.find(Row(), "missing") is None


async def test_clickhouse_connect_uses_asynch():
    with patch("asynch.Connection") as connection_cls:
        client = MagicMock()
        client.connect = AsyncMock()
        connection_cls.return_value = client
        clickhouse = ClickhouseDatabase(host="h", port=9000, username="u", password="p", database="d")
        await clickhouse.connect()
        connection_cls.assert_called_with(host="h", port=9000, user="u", password="p", database="d")
        client.connect.assert_awaited()
