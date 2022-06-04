from starlette.routing import Route
from server.api.users.endpoints import Login, Register, Refresh, Get_users

routes = [
    Route("/login", endpoint=Login),
    Route("/refresh", endpoint=Refresh),
    Route("/register", endpoint=Register),
    Route("/list", endpoint=Get_users)
]
