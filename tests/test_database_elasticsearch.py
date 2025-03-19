from elasticsearch import Elasticsearch

from elasticsearch.helpers import bulk
from uuid import uuid4



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







class Table:
    def __init__(self, es_client, table_name):
        self.es = es_client
        self.table_name = table_name

    def insert_one(self, record):
        doc_id = record.id or str(uuid4())
        doc = {k: v for k, v in record.to_dict().items() if k != "id"}
        self.es.index(index=self.table_name, id=doc_id, body=doc)
        return doc_id

    def insert_many(self, records):
        actions = [
            {
                "_index": self.table_name,
                "_id": record.id or str(uuid4()),
                "_source": {k: v for k, v in record.to_dict().items() if k != "id"}
            }
            for record in records
        ]
        bulk(self.es, actions)

    def update_one(self, record_id, updates):
        # Pass updates in the document's body, and specify the ID as a parameter
        self.es.update(index=self.table_name, id=record_id, body={"doc": updates})

    def update_many(self, records, updates):
        # Bulk update, specifying the ID as a parameter, not in the document
        actions = [
            {
                "_op_type": "update",
                "_index": self.table_name,
                "_id": record.id,  # Assuming each record has an id attribute
                "doc": updates
            }
            for record in records
        ]
        bulk(self.es, actions)

    def delete_one(self, record_id):
        # Specify the ID as a parameter
        self.es.delete(index=self.table_name, id=record_id)

    def delete_many(self, records):
        # Bulk delete, specifying each document ID
        actions = [
            {
                "_op_type": "delete",
                "_index": self.table_name,
                "_id": record.id  # Assuming each record has an id attribute
            }
            for record in records
        ]
        bulk(self.es, actions)







class ElasticORM:
    def __init__(self, host="localhost", port=9200, scheme="http", username=None, password=None):
        #self.es = Elasticsearch(
        #        [{"host": host, "port": port, "scheme": scheme}],
        #    basic_auth=(username, password) if username and password else None
        #)
        self.es = Elasticsearch(hosts=['https://elastic.dmz.ialoc.in'], timeout=300, basic_auth=(username, password))

    def __getattr__(self, table_name):
        """Dynamically access a table (index) as an attribute, e.g., `database.users`."""
        return Table(self.es, table_name)

    def create_table(self, table_name, mappings=None, settings=None):
        """Create an Elasticsearch index (table) with optional mappings and settings."""
        body = {}
        if mappings:
            body["mappings"] = mappings
        if settings:
            body["settings"] = settings

        try:
            # Only pass body if mappings or settings are provided
            if body:
                response = self.es.options(ignore_status=[400]).indices.create(index=table_name, body=body)
            else:
                response = self.es.options(ignore_status=[400]).indices.create(index=table_name)
            
            print(f"Index creation response: {response}")
        except Exception as e:
            print(f"Failed to create index {table_name}: {e}")

    def delete_table(self, table_name):
        """Delete an Elasticsearch index (table)."""
        self.es.indices.delete(index=table_name, ignore=[400, 404])  # Ignores errors if the index does not exist

    def list_tables(self):
        """List all existing indices (tables) in the Elasticsearch instance."""
        try:
            indices = self.es.cat.indices(format="json")
            index_names = [index["index"] for index in indices]
            print("Existing indices (tables):", index_names)
            return index_names
        except Exception as e:
            print(f"Failed to list indices: {e}")
            return []





#!/usr/bin/env python3
from tests.test_database_elasticsearch import ElasticORM
from future.models import Record
from uuid import uuid4
import socket


database = ElasticORM(
    host="elastic.dmz.ialoc.in",
    port=9200,
    username="elastic",
    password="elastic",
    scheme="https"
)

columns = {
    "properties": {
        "name": {
            "type": "text"
        },
        "uuid": {
            "type": "keyword"
        }
    }
}
#database.create_table("users", mappings=columns)

# Access the "users" table (index) for data operations
users = database.users

# Insert one record
record = Record(name="test", id=9, uuid="asdasd")
users.insert_one(record)

# Insert multiple records
records = [Record(name=f"test{i}", id=i, uuid=str(uuid4())) for i in range(10)]

users.insert_many(records)

# Update a record
users.update_one(9, {"name": "updated_test"})

# Delete a table (index)
#database.delete_table("users")

database.list_tables()





from elasticsearch import Elasticsearch
from urllib.parse import unquote as urldecode
from collections import Counter
import json


def public_search(self, type, query):
    if len(query) < 3:
        return {'error': 'Invalid query length. Must be 3 chars or more.'}

    if not type in self.ALLOWED_FIELDS:
        return {'error': 'Invalid search type.'}

    client = Elasticsearch(hosts=['10.30.1.39:9200'], timeout=300)

    query = urldecode(query)
    full_query = []

    full_query = {
        "query": {
            'term': {
                f'{type}.keyword': query
            }
        }
    }

    # Do the search and prepare results
    results = client.search(index="*", body=full_query, size=5)

    # Generate the response
    response = {}
    response['time'] = f"{results['took']} ms" # TODO: Fix me
    response['hits'] = len(results['hits']['hits'])
    response['matches'] = Counter(k['_index'] for k in results['hits']['hits'] if k.get('_index'))
    
    """
    for row in results:
        #tmp = row['_source']
        #tmp['leak'] = row['_index']
        tmp = {}
        tmp[row['_index']] = len(results) # TODO: Fixme lol. Should be amount of matches per database.
        response.append(tmp)
    """
    #return json.dumps(response, indent=4, sort_keys=False)
    return self.response.json(response, status=200)



class ElasticsearchModel:
    _index = "default"
    es = Elasticsearch(hosts=['10.30.1.39:9200'], timeout=300)
    ALLOWED_FIELDS = ['name', 'email']

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        if hasattr(self, 'id') and self.id:
            self.es.index(index=self._index, id=self.id, body=self.to_dict())
        else:
            response = self.es.index(index=self._index, body=self.to_dict())
            self.id = response['_id']

    def to_dict(self):
        return {attr: getattr(self, attr) for attr in dir(self)
                if not attr.startswith('_') and not callable(getattr(self, attr))}

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    def delete(self):
        if hasattr(self, 'id') and self.id:
            self.es.delete(index=self._index, id=self.id)

    def public_search(self, type, query):
        if len(query) < 3:
            return json.dumps({'error': 'Invalid query length. Must be 3 chars or more.'}, indent=4)
        if type not in self.ALLOWED_FIELDS:
            return json.dumps({'error': 'Invalid search type.'}, indent=4)
        query = urldecode(query)
        full_query = {
            "query": {
                'term': {
                    f'{type}.keyword': query
                }
            }
        }
        results = self.es.search(index=self._index, body=full_query, size=5)
        response = {
            'time': f"{results['took']} ms",
            'hits': len(results['hits']['hits']),
            'matches': Counter(k['_index'] for k in results['hits']['hits'] if k.get('_index'))
        }
        return json.dumps(response, indent=4)

    def get_record(id, index):
        try:
            result = ElasticsearchModel.es.get(index=index, id=id)
            if result['found']:
                return result['_source']
        except Exception as e:
            print(f"Error retrieving id {id}: {e}")
        return None

    def count_records(index):
        try:
            result = ElasticsearchModel.es.count(index=index)
            return f"{result['count']:,}"
        except Exception as e:
            print(f"Error counting records in index {index}: {e}")
        return "Error"


# Example usage of the class
class User(ElasticsearchModel):
    _index = "users"

    def __init__(self, name, email, password, id=None):
        super().__init__(name=name, email=email, password=password, id=id)

# Actions on User instance
user = User(name="John Doe", email="john.doe@example.com", password="secure123")
user.save()  # Create or update user
user_info = ElasticsearchModel.get_record(user.id, User._index)  # Retrieve user by ID
print(user_info)
user.update(name="John Updated Doe")  # Update user's name
user.delete()  # Delete the user
total_records = ElasticsearchModel.count_records(User._index)  # Get total records
print(total_records)
