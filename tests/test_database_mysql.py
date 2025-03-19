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