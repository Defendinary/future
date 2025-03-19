#!/usr/bin/env python3

import strawberry
from typing import List

from future.application import Future, Lifespan
from future.routing import Route
from future.request import Request
from future.response import JSONResponse

# 🔹 Mock Database
users_db = [
    {"id": "1", "name": "Alice", "email": "alice@example.com"},
    {"id": "2", "name": "Bob", "email": "bob@example.com"},
]

posts_db = [
    {"id": "101", "title": "GraphQL vs REST", "content": "GraphQL is amazing!", "author_id": "1"},
    {"id": "102", "title": "Strawberry Rocks", "content": "Strawberry is great for Python!", "author_id": "2"},
]

# 🔹 Define GraphQL Types (Manually, No Decorators)
UserType = strawberry.type(
    "User",
    fields=[
        strawberry.field("id", strawberry.ID),
        strawberry.field("name", str),
        strawberry.field("email", str),
    ],
)

PostType = strawberry.type(
    "Post",
    fields=[
        strawberry.field("id", strawberry.ID),
        strawberry.field("title", str),
        strawberry.field("content", str),
        strawberry.field("author", UserType),
    ],
)

# 🔹 Define Resolvers
def resolve_users() -> List[UserType]:
    return [UserType(id=u["id"], name=u["name"], email=u["email"]) for u in users_db]

def resolve_posts() -> List[PostType]:
    return [PostType(id=p["id"], title=p["title"], content=p["content"],
                     author=next(UserType(id=u["id"], name=u["name"], email=u["email"])
                                 for u in users_db if u["id"] == p["author_id"]))
            for p in posts_db]

# 🔹 Define Query Type (Manually)
QueryType = strawberry.type(
    "Query",
    fields=[
        strawberry.field("users", List[UserType], resolve_users),
        strawberry.field("posts", List[PostType], resolve_posts),
    ],
)

# 🔹 ✅ Create Schema (Official `strawberry.Schema()` API)
schema = strawberry.Schema(query=QueryType)

# 🔹 Future Framework Setup
app = Future(lifespan=Lifespan, name="Future", debug=True, domain="example.com:8000")

async def get_user_posts(request: Request):
    """REST endpoint that internally queries GraphQL."""
    
    graphql_query = """
    {
        posts {
            id
            title
            content
            author {
                name
                email
            }
        }
    }
    """
    
    result = schema.execute_sync(graphql_query)  # ✅ Official way to execute queries
    
    return JSONResponse(result.data)

# 🔹 Define Routes
routes = [
    Route(path="/userposts", methods=["GET"], endpoint=get_user_posts, name="GetUserPosts"),
]

app.add_routes(routes)

# 🔹 Run Future App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, workers=1)
