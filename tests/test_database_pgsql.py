from unittest.mock import patch, MagicMock
import unittest
import psycopg2

class TestPostgreSQL(unittest.TestCase):
    @patch("psycopg2.connect")
    def test_query(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [(1, "data")]
        mock_cursor.description = (("id",), ("value",))  # Prevents AttributeError on fetch

        conn = psycopg2.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test")
        result = cursor.fetchall()

        self.assertEqual(result, [(1, "data")])
        mock_cursor.execute.assert_called_with("SELECT * FROM test")
