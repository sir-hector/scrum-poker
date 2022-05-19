import base64
import binascii
from os import getenv

import uvicorn
import jwt
from starlette.applications import Starlette
from starlette.authentication import AuthenticationBackend, SimpleUser, AuthCredentials, AuthenticationError
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.routing import Mount
from server.api import routes as api_routes

routes = [
    Mount("/api", routes=api_routes, name="api"),
]


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return

        token = conn.headers["Authorization"]
        try:
            payload = jwt.decode(token, key=getenv('SECRET_KEY'), algorithms='HS256')
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(str(e))

        return AuthCredentials(["authenticated"]), SimpleUser(username=payload['user_id'])


middleware = [
    Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())
]


def run():
    app = Starlette(debug=True, routes=routes, middleware=middleware)
    uvicorn.run(app)
