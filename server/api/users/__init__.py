from starlette.endpoints import HTTPEndpoint
from starlette.responses import PlainTextResponse
from starlette.routing import Route


class Login(HTTPEndpoint):
    async def get(self, request):
        return PlainTextResponse(f"Hello, world!")


routes = [
    Route("/", Login)
]
