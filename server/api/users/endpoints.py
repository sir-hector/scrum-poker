import datetime
import json
from json import JSONDecodeError
import jwt
from os import getenv
from commands.users import register, login_user, list_all
from starlette.endpoints import HTTPEndpoint
from starlette.responses import PlainTextResponse, JSONResponse
from database.sql import SessionLocal, engine
from users.exceptions import LoginException, UsersExceptions
from starlette.authentication import requires


class Login(HTTPEndpoint):
    async def post(self, request):
        try:
            payload = await request.json()
        except JSONDecodeError:
            return JSONResponse({'error': 'cannot_parse_request_body'}, status_code=400)

        session = SessionLocal(bind=engine)
        try:
            login = payload['login']
            password = payload['password']
            user_id = login_user(session, login, password)
        except LoginException as err:
            return JSONResponse({'error': f'{err}'}, status_code=401)
        except UsersExceptions as err:
            return JSONResponse({'error': f'{err}'}, status_code=400)

        token = jwt.encode(
            {'user_id': f'{user_id}', 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)},
            getenv('SECRET_KEY'))

        return JSONResponse({"token": f'{token}'}, status_code=200)


class Register(HTTPEndpoint):
    async def post(self, request):
        try:
            payload = await request.json()
        except JSONDecodeError:
            return JSONResponse({'error': 'cannot_parse_request_body'}, status_code=400)
        session = SessionLocal(bind=engine)
        try:
            login = payload['login']
            password = payload['password']
            register(session, login, password)
        except UsersExceptions as err:
            return JSONResponse({'error': f'{err}'}, status_code=400)

        return JSONResponse({}, status_code=200)


class Refresh(HTTPEndpoint):
    @requires('authenticated', status_code=401)
    async def post(self, request):
        user_id = request.user.display_name
        token = jwt.encode(
            {'user_id': f'{user_id}', 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)},
            getenv('SECRET_KEY'))
        return JSONResponse({"token": f'{token}'}, status_code=200)


class Get_users(HTTPEndpoint):
    @requires('authenticated', status_code=401)
    async def get(self, request):
        session = SessionLocal(bind=engine)
        users = list_all(session)
        json_string = json.dumps([dict(ob) for ob in users])
        return PlainTextResponse(json_string, status_code=200)
