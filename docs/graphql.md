# GraphQL
`GraphQLController.query` is a search endpoint. The client posts **field terms**, not a GraphQL document. The controller runs one Active Record query per term, unions hits by id, then Strawberry shapes the JSON (`GetEverything`).

Register the route yourself. There is no `app.add_graphql_route` and no `GRAPHQL_SCHEMA` config key.

```python
from future.controllers.GraphQLController import GraphQLController
from future.routing import Post, RouteGroup

RouteGroup(
    name="Search",
    routes=[
        Post("/graphql", GraphQLController.query, "graphql"),
    ],
)
```

## Request
`POST` a JSON object. At least one search field is required. `limit` is optional (default `20`, clamped to `1`–`100`).

| Field | Looks up |
|-------|----------|
| `email` | `UserModel.where("email", …)` |
| `name` | `UserModel.where("name", …)` |
| `id` | `UserModel` and `PostModel` by `id` |
| `title` | `PostModel.where("title", …)` |
| `content` | `PostModel.where("content", …)` |
| `author_id` | `PostModel.where("author_id", …)` |
| `limit` | Max rows **per term** |

Terms are **separate** searches. `{"name": "Alice", "email": "bob@example.com"}` can return both users.

```bash
curl -s -X POST http://127.0.0.1:8000/graphql \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","title":"Strawberry Rocks"}'
```

## Response
Always the `GetEverything` shape. Posts include `author` (eager-loaded).

```json
{
  "data": {
    "users": [{"id": "1", "name": "Alice", "email": "alice@example.com"}],
    "posts": [{
      "id": "102",
      "title": "Strawberry Rocks",
      "content": "Strawberry is great for Python!",
      "author": {"id": "2", "name": "Bob", "email": "bob@example.com"}
    }]
  }
}
```

Missing / empty terms → `400` `{"errors": ["at least one search field required"]}`. Non-object JSON or a non-integer `limit` → `400` with `errors`.

## Schema
Types are `UserType = strawberry.type(UserModel)` and `PostType = strawberry.type(PostModel)` on the controller. The nested `Query` class annotates `list[UserModel]` / `list[PostModel]` because `UserType` is not in that class scope; resolvers still return the Strawberry types.

The in-repo models are the demo (`UserModel`, `PostModel`). An app with other tables writes its own controller the same way: search terms in the action, Strawberry only for the payload shape.
