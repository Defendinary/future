from unittest.mock import patch, MagicMock
import unittest
from pymongo import MongoClient

class TestMongoDB(unittest.TestCase):
    @patch("pymongo.MongoClient")
    def test_find(self, mock_mongo):
        mock_db = MagicMock()
        mock_mongo.return_value = mock_db
        mock_collection = mock_db.test.collection
        mock_collection.find.return_value = [{"field": "value"}]
        
        client = MongoClient()
        result = list(client.test.collection.find({}))
        self.assertEqual(result[0]["field"], "value")
