from unittest.mock import patch, MagicMock
import unittest
from clickhouse_driver import Client



from unittest.mock import patch, MagicMock
import unittest
from elasticsearch import Elasticsearch

class TestElastic(unittest.TestCase):
    @patch("elasticsearch.Elasticsearch.search")
    def test_search(self, mock_search):
        mock_search.return_value = {"hits": {"hits": [{"_source": {"field": "value"}}]}}
        es = Elasticsearch()
        result = es.search(index="test", body={})
        self.assertEqual(result["hits"]["hits"][0]["_source"]["field"], "value")









class TestClickHouse(unittest.TestCase):
    @patch("clickhouse_driver.Client.execute")
    def test_query(self, mock_execute):
        mock_execute.return_value = [(1, "data")]
        client = Client("localhost")
        result = client.execute("SELECT * FROM test")
        self.assertEqual(result, [(1, "data")])


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




from future.database import Database
from future.models import User



from unittest.mock import patch, MagicMock
import unittest
import mysql.connector

class TestMySQL(unittest.TestCase):
    @patch("mysql.connector.connect")
    def test_query(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [(1, "data")]
        mock_cursor.description = (("id",), ("value",))  # Prevents AttributeError on fetch

        conn = mysql.connector.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test")
        result = cursor.fetchall()

        self.assertEqual(result, [(1, "data")])
        mock_cursor.execute.assert_called_with("SELECT * FROM test")





# read: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.async_sessionmaker
#self.session.add(entity)
#self.session.commit()
#self.session.rollback()
#self.session.close()
#self.session.flush()


database = Database(
    driver="mysql",
    host="10.0.0.69",
    port=3306,
    username="user",
    password="lol123",
    database="test",
    options="",
).session()

# FIXME: Create the table in the database - migrations?
#Model.metadata.create_all(engine, checkfirst=True)

# Add a user
new_user = User(name='John Doe', email='johndoe@example.com')
database.add(new_user)
database.commit()

# Query all users
users = database.query(User).all()

# Update a user
user = database.query(User).filter(User.name == 'John Doe').first()
user.email = 'newemail@example.com'
database.commit()

# Delete a user
user = database.query(User).filter(User.name == 'John Doe').first()
database.delete(user)
database.commit()

# Custom query
#people = database.execute("SELECT * FROM people WHERE name = :name", {'name': 'John Doe'}).scalars().all()





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




