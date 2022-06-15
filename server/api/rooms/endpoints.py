import json
from http.client import HTTPException
from json import JSONDecodeError
from os import getenv

from starlette.authentication import requires
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse, PlainTextResponse

from commands.rooms import list_all, create_room, join_room, get_room_details, change_room_topic, get_all_votes, put_vote

from database import database


class GetRooms(HTTPEndpoint):
    @requires('authenticated', status_code=401)
    async def get(self, request):
        user_id = request.scope["user"].username
        db = database.get_database(getenv('DB_NAME'))
        rooms = list_all(db, user_id)
        print(rooms)
        json_string = json.dumps([dict(ob) for ob in rooms])
        return PlainTextResponse(json_string, status_code=200)


class CreateRoom(HTTPEndpoint):
    @requires('authenticated', status_code=401)
    async def post(self, request):
        try:
            payload = await request.json()
        except JSONDecodeError:
            return JSONResponse({'error': 'cannot_parse_request_body'}, status_code=400)

        db = database.get_database(getenv('DB_NAME'))

        try:
            name = payload['name']
            password = payload['password']
            user_id = request.scope["user"].username
            create_room(db, name, password, user_id)
        except Exception as err:
            return JSONResponse({'error': f'{err}'}, status_code=400)

        return JSONResponse({}, status_code=200)


class JoinRoom(HTTPEndpoint):
    @requires('authenticated', status_code=401)
    async def post(self, request):
        room_id = request.path_params['id']
        try:
            payload = await request.json()
        except JSONDecodeError:
            return JSONResponse({'error': 'cannot_parse_request_body'}, status_code=400)

        db = database.get_database(getenv('DB_NAME'))

        try:
            password = payload['password']
            user_id = request.scope["user"].username
            join_room(db, room_id, password, user_id)
        except Exception as err:
            return JSONResponse({'error': f'{err}'}, status_code=400)

        return JSONResponse({}, status_code=200)


class GetRoomDetails(HTTPEndpoint):
    @requires('authenticated', status_code=401)
    async def get(self, request):
        room_id = request.path_params['id']
        db = database.get_database(getenv('DB_NAME'))
        try:
            user_id = request.scope["user"].username
            room = get_room_details(db, room_id, user_id)
        except Exception as err:
            return JSONResponse({'error': f'{err}'}, status_code=400)
        room = room.json()
        return PlainTextResponse(room, status_code=200)

    @requires('authenticated', status_code=401)
    async def patch(self, request):
        room_id = request.path_params['id']
        try:
            payload = await request.json()
        except JSONDecodeError:
            return JSONResponse({'error': 'cannot_parse_request_body'}, status_code=400)

        db = database.get_database(getenv('DB_NAME'))
        topic = ''
        password = ''
        if 'topic' in payload:
            topic = payload['topic']
        if 'password' in payload:
            password = payload['password']

        user_id = request.scope["user"].username
        try:
            room = change_room_topic(db, room_id, user_id, topic, password)
        except Exception as err:
            return JSONResponse({'error': f'{err}'}, status_code=400)
        room = room.json()
        return PlainTextResponse(room, status_code=200)


class RoomVotes(HTTPEndpoint):
    @requires('authenticated', status_code=401)
    async def get(self, request):
        user_id = request.scope["user"].username
        room_id = request.path_params['id']
        db = database.get_database(getenv('DB_NAME'))

        try:
            votes = get_all_votes(db, user_id, room_id)
        except Exception as err:
            return JSONResponse({'error': f'{err}'}, status_code=400)
        print(votes)
        if votes is not None:
            votes = votes.json()
        return PlainTextResponse(votes, status_code=200)

    @requires('authenticated', status_code=401)
    async def put(self, request):
        user_id = request.scope["user"].username
        room_id = request.path_params['id']
        db = database.get_database(getenv('DB_NAME'))
        try:
            payload = await request.json()
        except JSONDecodeError:
            return JSONResponse({'error': 'cannot_parse_request_body'}, status_code=400)
        try:
            vote = payload['vote']
            put_vote(db, user_id, room_id, vote)
        except Exception as err:
            return JSONResponse({'error': f'{err}'}, status_code=400)

        return JSONResponse({}, status_code=200)

