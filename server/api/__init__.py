from starlette.routing import Mount
from server.api.users import routes as users_routes
from server.api.rooms import routes as rooms_routes

routes = [
    Mount("/users", routes=users_routes),
    Mount("/rooms", routes=rooms_routes)
]
