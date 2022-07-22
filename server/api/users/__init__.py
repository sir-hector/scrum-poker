from starlette.routing import Route
from server.api.users.endpoints import Login, Register, Refresh

routes = [
    Route("/login", endpoint=Login),
    Route("/refresh", endpoint=Refresh),
    Route("/register", endpoint=Register)
]
