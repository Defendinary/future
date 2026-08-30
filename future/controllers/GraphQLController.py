from textwrap import dedent

import strawberry
from strawberry.schema.config import StrawberryConfig

from future.interfaces.IController import IController
from future.models.PostModel import PostModel
from future.models.UserModel import UserModel
from future.response import Response


class GraphQLController(IController):
    # Shapes GraphQL uses to consolidate controller search hits. The client never sends these.
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
                        id
                        name
                        email
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

    db_users = [
        {"id": "1", "name": "Alice", "email": "alice@example.com"},
        {"id": "2", "name": "Bob", "email": "bob@example.com"},
        {"id": "3", "name": "Charlie", "email": "charlie@example.com"},
    ]

    db_posts = [
        {"id": "101", "title": "GraphQL vs REST", "content": "GraphQL is amazing!", "author_id": "1"},
        {"id": "102", "title": "Strawberry Rocks", "content": "Strawberry is great for Python!", "author_id": "2"},
    ]

    UserType = strawberry.type(UserModel)
    PostType = strawberry.type(PostModel)

    async def resolve_users(self, info: strawberry.Info) -> list[UserType]:  # type: ignore[misc,valid-type]
        rows = info.context.get("users") or []
        return [GraphQLController.UserType(id=u.id, name=u.name, email=u.email) for u in rows]

    async def resolve_posts(self, info: strawberry.Info) -> list[PostType]:  # type: ignore[misc,valid-type]
        rows = info.context.get("posts") or []
        posts = []
        for p in rows:
            post = GraphQLController.PostType(id=p.id, title=p.title, content=p.content, author_id=p.author_id)
            post.author = p.author
            posts.append(post)
        return posts

    class Query:
        users: list[UserModel]
        posts: list[PostModel]

    Query.users = strawberry.field(resolver=resolve_users)
    Query.posts = strawberry.field(resolver=resolve_posts)
    schema = strawberry.Schema(query=strawberry.type(Query), config=StrawberryConfig(auto_camel_case=False))

    async def query(self) -> Response:
        body = await self.request.json()
        if not isinstance(body, dict):
            return self.response.json({"errors": ["JSON body required"]}, status=400)
        email = body.get("email")
        name = body.get("name")
        title = body.get("title")
        content = body.get("content")
        author_id = body.get("author_id")
        record_id = body.get("id")
        if not any(value not in (None, "") for value in (email, name, title, content, author_id, record_id)):
            return self.response.json({"errors": ["at least one search field required"]}, status=400)
        try:
            limit = min(max(int(body.get("limit", 20)), 1), 100)
        except (TypeError, ValueError):
            return self.response.json({"errors": ["limit must be an integer"]}, status=400)

        users_by_id = {}
        posts_by_id = {}
        if email not in (None, ""):
            for row in await UserModel.where("email", email).limit(limit).get():
                users_by_id[row.id] = row
        if name not in (None, ""):
            for row in await UserModel.where("name", name).limit(limit).get():
                users_by_id[row.id] = row
        if record_id not in (None, ""):
            for row in await UserModel.where("id", record_id).limit(limit).get():
                users_by_id[row.id] = row
            for row in await PostModel.where("id", record_id).limit(limit).get():
                posts_by_id[row.id] = row
        if title not in (None, ""):
            for row in await PostModel.where("title", title).limit(limit).get():
                posts_by_id[row.id] = row
        if content not in (None, ""):
            for row in await PostModel.where("content", content).limit(limit).get():
                posts_by_id[row.id] = row
        if author_id not in (None, ""):
            for row in await PostModel.where("author_id", author_id).limit(limit).get():
                posts_by_id[row.id] = row

        users = list(users_by_id.values())
        posts = list(posts_by_id.values())
        await UserModel.eager_load(posts, "author", UserModel, foreign_key="author_id")

        result = await GraphQLController.schema.execute(GraphQLController.queries["GetEverything"], context_value={"users": users, "posts": posts})
        payload = {"data": result.data}
        if result.errors:
            payload["errors"] = [str(error) for error in result.errors]
            return self.response.json(payload, status=400)
        return self.response.json(payload)
