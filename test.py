from future.application import Future, Lifespan
from future.controllers import WelcomeController
from future.middleware import ResponseCodeConfuser, TestMiddlewareRequest, TestMiddlewareResponse
from future.routing import RouteGroup, Get
#from enum import Enum


app = Future(lifespan=Lifespan, name="Future", debug=True, domain="example.com")

routes = [
    Get(path='/', endpoint=WelcomeController.ping, name="Ping"), #, middlewares=[TestMiddlewareRequest]),  # type: ignore[reportAttributeAccessIssue]

    RouteGroup(
        name="API",
        subdomain="api",
        prefix="/api",
        middlewares=[
            #ResponseCodeConfuser,
        ],
        routes=[
            Get(path='/', endpoint=WelcomeController.root, name="welcome"),  # type: ignore[reportAttributeAccessIssue]
            #Get(path='/users/<int:user_id>/<str:arg2>', endpoint=WelcomeController.args, name="getUserInfo"),  # type: ignore[reportAttributeAccessIssue]
            #Get(path="/api/cats/<int:cat_id>", endpoint=some_handler, name="get_cat"),  # type: ignore[reportAttributeAccessIssue]
            #Get(path="/api/dogs/<uuid:dog_id>", endpoint=some_handler, name="get_dog"),  # type: ignore[reportAttributeAccessIssue]
        ],
    ),
]

app.add_routes(routes=routes)
print(app.routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, workers=1)
