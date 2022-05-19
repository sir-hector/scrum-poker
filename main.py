import os
from getpass import getpass

import click
import uvicorn
from dotenv import load_dotenv
from os import getenv
import database.database
from users import user_service
from starlette.applications import Starlette
import server

load_dotenv()


def access(select, db):
    if select == 'L':
        name = input("Wprowadz imie: ")
        password = getpass("Wprowadź hasło: ")
        if user_service.login(db, name, password):
            grant()
            return
        else:
            program(db)
    else:
        name = input("Wprowadz imie: ")
        password = getpass("Wprowadź hasło: ")
        if not user_service.register(db, name, password):
            access('R', db)
        else:
            program(db)


def program(db):
    global select
    select = input("L - Logowanie, R = Rejestracja: ")
    if select != "L" and select != "R":
        program(db)
    else:
        access(select, db)


def grant():
    global granted
    granted = True

@click.group()
@click.pass_context
def run(ctx):
    db = database.database.get_database(getenv('DB_NAME'))
    ctx.obj={}
    ctx.obj['db'] = db

@run.command("run", help="run application")
def run_application():
    db = database.database.get_database(getenv('DB_NAME'))
    granted = False
    program(db)
    if granted:
        user_service.run(db)



@run.command("clear-db", help="Recreate DB")
def initialize_db():
    if os.stat(os.getenv('DB_NAME')):
        os.remove(os.getenv('DB_NAME'))
        db = database.database.get_database(getenv('DB_NAME'))
        database.database.initialize_db(db)

@run.command("run-as-server", help="run server")
def run_server():
    server.run()


run.add_command(user_service.user)

if __name__ == '__main__':
    run()
