from dotenv import load_dotenv
from os import getenv
import database.database
from users import user_service
load_dotenv()


def access(select, db):
    if select == 'L':
        if user_service.login(db):
            grant()
            return
        else:
            program(db)
    else:
        if not user_service.register(db):
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


if __name__ == '__main__':

    # database.database.cli()
    db = database.database.get_database(getenv('DB_NAME'))
    print(db)
    granted = False
    program(db)
    if granted:
        user_service.run(db)
