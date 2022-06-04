from starlette.routing import Route
from server.api.rooms.endpoints import GetRooms, CreateRoom, JoinRoom, GetRoomDetails, RoomVotes

routes = [
    Route("/my", endpoint=GetRooms),
    Route("/create", endpoint=CreateRoom),
    Route("/{id:int}/join", endpoint=JoinRoom),
    Route("/{id:int}", endpoint=GetRoomDetails),
    Route("/{id:int}/vote", endpoint=RoomVotes),
]
