import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount
from server.api import routes as api_routes

routes = [
    Mount("/api", routes=api_routes, name="api"),
]

def run():
    app = Starlette(debug=True, routes=routes)
    uvicorn.run(app)