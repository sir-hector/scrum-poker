from dotenv import load_dotenv
from os import getenv
import database.database
import users.user_service as service
import database.database as data
from users import user_service
load_dotenv()


def access(select, db2):
    if select == 'L':
        if user_service.login(db2):
            grant()
            return
        else:
            program(db2)
    else:
        if not user_service.register(db2):
            access('R', db2)
        else:
            program(db2)


def program(db2):
    global select
    select = input("L - Logowanie, R = Rejestracja: ")
    if select != "L" and select != "R":
        program(db2)
    else:
        access(select, db2)


def grant():
    global granted
    granted = True


if __name__ == '__main__':

    # database.database.cli()
    db2 = database.database.get_database(getenv('DB_NAME'))
    print(db2)
    db = data.Database('db.csv')
    db.check_db_exists()
    granted = False
    program(db2)
    if granted:
        user_service.run(db2)
