from unittest.mock import AsyncMock, MagicMock, patch

from future.databases.MongoDBDatabase import MongoDBDatabase
from future.interfaces.IModel import IModel


class Row(IModel):
    __table__ = "rows"


async def test_mongo_save_find():
    mongo = MongoDBDatabase(host="localhost", port=27017, username="", password="", database="db")
    collection = MagicMock()
    collection.replace_one = AsyncMock()
    collection.find_one = AsyncMock(return_value={"id": "1", "name": "n"})
    mongo.db = MagicMock()
    mongo.db.__getitem__.return_value = collection
    mongo.client = MagicMock()
    result = await mongo.save(Row(id="1", name="n"))
    assert result["status"] == "saved"
    collection.replace_one.assert_awaited()
    found = await mongo.find(Row(), "1")
    assert found is not None and found.name == "n"


async def test_mongo_find_missing_returns_none():
    mongo = MongoDBDatabase(host="localhost", port=27017, username="", password="", database="db")
    collection = MagicMock()
    collection.find_one = AsyncMock(return_value=None)
    mongo.db = MagicMock()
    mongo.db.__getitem__.return_value = collection
    mongo.client = MagicMock()
    assert await mongo.find(Row(), "missing") is None


async def test_mongo_connect_builds_uri():
    with patch("pymongo.AsyncMongoClient") as client_cls:
        client = MagicMock()
        client.__getitem__.return_value = MagicMock()
        client_cls.return_value = client
        mongo = MongoDBDatabase(host="h", port=27017, username="u", password="p", database="d")
        await mongo.connect()
        client_cls.assert_called_with("mongodb://u:p@h:27017/d")
        assert mongo.db is client["d"]
