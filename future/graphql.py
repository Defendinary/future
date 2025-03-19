import os
import sys
import logging
import logging.handlers
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
from ariadne import graphql_sync, EnumType, load_schema_from_path, make_executable_schema, ObjectType, ScalarType, SchemaDirectiveVisitor
from ariadne.explorer import ExplorerGraphiQL
from graphql import default_field_resolver, GraphQLError

# wsgi application instance to deploy app behind apache/gunicorn/nginx

"""
# GraphQL


Visit http://127.0.0.1:5000/graphql

To list all the users use this query
```graphql
query users {
    users {
        items {
            username
            id
            email
        }
    }
}
```

To test a mutation use this
```graphql
mutation reg {
    register (input: {
        username: "hello",
        password: "world",
        email: "hello@world.com"
    })
    {
        id
    }
}
```
"""


#app_path = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, app_path)
#schema_dirname, _filename = os.path.split(os.path.abspath(__file__))


# This is a function used by mutation. For demo purposes does not contain logic, only prints the inputs given from graphql

def UserRegistrationResolver(_, info, input=None):
    # Do somethign with the data inside the controller
    __import__('pprint').pprint(input)
    return { 'status': True, 'id': 1 }


def UserViewResolver(_, info, paging=None):
    list_of_users = [
        {'id': 1, 'username': 'user1', 'email': 'user1@example.com'},
        {'id': 2, 'username': 'user2', 'email': 'user2@example.com'},
        {'id': 3, 'username': 'user3', 'email': 'user3@example.com'},
        {'id': 4, 'username': 'user4', 'email': 'user4@example.com'},
        {'id': 5, 'username': 'user5', 'email': 'user5@example.com'}
    ]
    result = {
        'items': list_of_users
    }
    return result




def UserContext(request):
    context = {
        'request': request,
        'user': "Smet",
        'role': None
    }
    # Do some logic for user context, and return the context object If the user 
    # is None, the directive throws error or missing token Change the value of
    # User to something if you want to see email field
    return context


class AuthDirective(SchemaDirectiveVisitor):
    def visit_field_definition(self, field, object_type):
        original_resolver = field.resolve or default_field_resolver

        def resolve_is_authenticated(obj, info, **kwargs):
            auth = info.context.get('user')
            if not auth:
                raise GraphQLError("No Token or invalid token")
            result = original_resolver(obj, info, **kwargs)
            return result

        field.resolve = resolve_is_authenticated
        return field



base_types = load_schema_from_path('./base.graphql')
root_query = load_schema_from_path('./root.query.graphql')
root_mutation = load_schema_from_path('./root.mutation.graphql')
paging_types = load_schema_from_path('./paging.graphql')
directive_type = load_schema_from_path('./directives.graphql')
user_types = load_schema_from_path('./user.graphql')


# Create definition list
type_defs = [
    base_types,
    root_query,
    root_mutation,
    paging_types,
    directive_type,
    user_types,
]


# Initialize schema objects (general).
mutation = ObjectType('Mutation')
root = ObjectType('Query')

# Associate resolvers with query fields.
root.set_field('users', UserViewResolver)

# Associate resolvers with mutation fields.
mutation.set_field('register', UserRegistrationResolver)

# Create Directive associations
directives = {
    'isAuthenticated': AuthDirective
}

# Create schema object list
schema_objects = [
    mutation,
    root,
    ObjectType('Paging'),
    ObjectType('ResponsePayload')
]

schema = make_executable_schema(type_defs, schema_objects, directives=directives)


app = Flask(__name__)

CORS(app, origins="*")

# Fix for relative path for instance, to load configuration # what in the batshit crazy is this
#app.config.root_path = app.instance_path
#app.config.from_pyfile("config.py")

config = {
    "BASE_DIR": os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
    "LOG_FILE": "/tmp/spacectf.log",
    "LOG_SIZE": 1024*1024,
    "LOG_LEVEL": logging.DEBUG,
    "HOST": '0.0.0.0'
}

app.config = config

# Configure Logging
handler = logging.handlers.RotatingFileHandler(app.config["LOG_FILE"], maxBytes=app.config["LOG_SIZE"])
handler.setLevel(app.config["LOG_LEVEL"])
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s [%(pathname)s at %(lineno)s]: %(message)s", "%Y-%m-%d %H:%M:%S"))
app.logger.addHandler(handler)





@app.route("/")
def index():
    data = { "status": "Running" }
    status_code = 200
    return jsonify(data), status_code


@app.route('/graphql', methods=['POST', 'OPTION'])
@app.route('/api', methods=['POST', 'OPTION'])
@cross_origin()
def graphql_server():
    data = request.get_json()

    success, result = graphql_sync(
        schema,
        data,
        context_value=UserContext(request),
        debug=app.debug,
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


# Serve an graphql Explorer via regular get requests. This makes it easy to write queries and mutation during development
@app.route('/graphql', methods=['GET'])
def graphql_playgroud():
    explorer_html = ExplorerGraphiQL().html(None)
    return explorer_html, 200
