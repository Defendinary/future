from future.application import Future, Lifespan
from future.controllers import WelcomeController, DebugController
from future.middleware import ResponseCodeConfuser, TestMiddlewareRequest, TestMiddlewareResponse
from future.routing import RouteGroup, Get
from future.graphql import graphql_handler


routes = [
    Get(path='/', endpoint=WelcomeController.root, name="Welcome"), #, middlewares=[TestMiddlewareRequest]),  # type: ignore[reportAttributeAccessIssue]
    Get(path='/test', endpoint=DebugController.test, name="test"),  # type: ignore[reportAttributeAccessIssue]
    Get(path="/graphql", endpoint=graphql_handler, name="graphql"),   # type: ignore[reportAttributeAccessIssue]
    RouteGroup(
        name="API",
        subdomain="api",
        prefix="/api",
        middlewares=[
            #TestMiddlewareRequest,
            #TestMiddlewareResponse,
            #ResponseCodeConfuser,
        ],
        routes=[
            Get(path='/', endpoint=WelcomeController.ping, name="Pong"),  # type: ignore[reportAttributeAccessIssue]
            #Get(path='/users/<int:user_id>/<str:arg2>', endpoint=WelcomeController.args, name="getUserInfo"),  # type: ignore[reportAttributeAccessIssue]
            #Get(path="/api/cats/<int:cat_id>", endpoint=some_handler, name="get_cat"),  # type: ignore[reportAttributeAccessIssue]
            #Get(path="/api/dogs/<uuid:dog_id>", endpoint=some_handler, name="get_dog"),  # type: ignore[reportAttributeAccessIssue]
        ],
    ),
]

config = {
    "APP_NAME": "Future",
    "APP_DOMAIN": "example.com",
    "APP_DEBUG": True,
} 

# Remove certain options from Future __init__() and force user to add_config() instead?
app = Future(lifespan=Lifespan, name=config["APP_NAME"], debug=config["APP_DEBUG"], domain=config["APP_DOMAIN"])
app.add_config(config)
app.add_routes(routes=routes)
#print(app.routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, workers=1)
