from unittest.mock import patch, MagicMock
import unittest
from clickhouse_driver import Client

class TestClickHouse(unittest.TestCase):
    @patch("clickhouse_driver.Client.execute")
    def test_query(self, mock_execute):
        mock_execute.return_value = [(1, "data")]
        client = Client("localhost")
        result = client.execute("SELECT * FROM test")
        self.assertEqual(result, [(1, "data")])
