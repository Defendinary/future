from typing import List
import strawberry
import json
from future.request import Request
from future.response import Response
from textwrap import dedent


# Sample data
users_db = [
    {"id": "1", "name": "Alice", "email": "alice@example.com"},
    {"id": "2", "name": "Bob", "email": "bob@example.com"},
]

posts_db = [
    {"id": "101", "title": "GraphQL vs REST", "content": "GraphQL is amazing!", "author_id": "1"},
    {"id": "102", "title": "Strawberry Rocks", "content": "Strawberry is great for Python!", "author_id": "2"},
]


# GraphQL queries
queries = {

    "GetEverything": dedent("""
        query GetEverything {
            users {
                id
                name
                email
            }
            posts {
                id
                title
                content
                author {
                    name
                }
            }
        }
    """),  # type: ignore[reportGeneralTypeIssues]
    
    "GetAllUsers": dedent("""
        query GetAllUsers {
            users {
                id
                name
                email
            }
        }  
    """),  # type: ignore[reportGeneralTypeIssues]
    

    "GetAllPosts": dedent("""
        query GetAllPosts {
            posts {
                id
                title
                content
                author {
                id
                name
                email
            }
        }
    """),  # type: ignore[reportGeneralTypeIssues]

    "GetAllUsers": dedent("""
        query GetAllUsers {
            users {
                id
                name
                email
            }
        }
    """),  # type: ignore[reportGeneralTypeIssues]

    "GetPostsWithAuthors": dedent("""
        query GetPostsWithAuthors {
            posts {
                id
                title
                content
                author {
                    name
                    email
                }
            }
        """),  # type: ignore[reportGeneralTypeIssues]
    
    "GetEverything": dedent("""
        query GetEverything {
            users {
                id
                name
                email
            }
            posts {
                id
                title
                content
                author {
                    name
                }
            }
        }
    """),  # type: ignore[reportGeneralTypeIssues]
    
    "GetTitlesAndAuthors": dedent("""
        query GetTitlesAndAuthors {
            posts {
                title
                author {
                    name
                }
            }
        """),  # type: ignore[reportGeneralTypeIssues]
    
    "GetEmails": dedent("""
        query GetEmails {
            users {
                email
            }   
        }
    """),  # type: ignore[reportGeneralTypeIssues]

    "GetEmails": dedent("""
        query GetEmails {
            users {
                email
            }
        }
    """),  # type: ignore[reportGeneralTypeIssues]

}



# Define types with fields
class User:
    id: strawberry.ID = strawberry.field()
    name: str = strawberry.field()
    email: str = strawberry.field()

class Post:
    id: strawberry.ID = strawberry.field()
    title: str = strawberry.field()
    content: str = strawberry.field()
    author: 'User' = strawberry.field()



# Convert to Strawberry types
UserType = strawberry.type(User)
PostType = strawberry.type(Post)



# Define resolvers
async def resolve_users() -> List[UserType]:
    return [
        UserType(id=u["id"], name=u["name"], email=u["email"]) 
        for u in users_db
    ]

async def resolve_posts() -> List[PostType]:
    posts = []
    for p in posts_db:
        author = next(u for u in users_db if u["id"] == p["author_id"])
        user = UserType(id=author["id"], name=author["name"], email=author["email"])
        post = PostType(
            id=p["id"],
            title=p["title"],
            content=p["content"],
            author=user
        )
        posts.append(post)
    return posts



# Create Query type
class Query:
    users = strawberry.field(resolver=resolve_users)
    posts = strawberry.field(resolver=resolve_posts)





# Create schema
schema = strawberry.Schema(query=strawberry.type(Query))


# GraphQL handler
async def graphql_handler(request: Request) -> Response:
    body = await request.body()
    
    if not body:
        query = queries["GetEverything"]
    else:
        try:
            query_data = json.loads(body)
            query = query_data["query"]
        except (json.JSONDecodeError, KeyError):
            return Response(
                body=json.dumps({"error": "Invalid JSON or missing query"}).encode(),
                status=400
            )

    result = await schema.execute(query)
    if result.errors:
        return Response(
            body=json.dumps({"errors": [str(error) for error in result.errors]}).encode(),
            status=400
        )
    
    return Response(body=json.dumps(result.data).encode())

