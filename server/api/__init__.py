from starlette.routing import Mount
from server.api.users import routes as users_routes

routes = [
    Mount("/users", routes=users_routes)
]
