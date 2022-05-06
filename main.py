from dotenv import load_dotenv
from os import getenv
import database.database
import users.user_service as service
import database.database as data
load_dotenv()

def access(select):
    if select == 'L':
        if user_service.login():
            grant()
            return
        else:
            program()
    else:
        if not user_service.register():
            access('R')
        else:
            program()


def program():
    global select
    select = input("L - Logowanie, R = Rejestracja: ")
    if select != "L" and select != "R":
        program()
    else:
        access(select)


def grant():
    global granted
    granted = True


if __name__ == '__main__':

    # database.database.cli()
    db2 = database.database.get_database(getenv('DB_NAME'))
    print(db2)
    db = data.Database('db.csv')
    db.check_db_exists()
    user_service = service.UserService()
    granted = False
    program()
    if granted:
        user_service.run()
