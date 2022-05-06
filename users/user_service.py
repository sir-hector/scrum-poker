import re
import bcrypt
import config
import database.database
from getpass import getpass
from users import rooms_service


def delete_user(db: database.database):
    name = input("Podaj nazwe użytkownika do usunięcia: ")
    db.delete('users', name)


def find_users(db: database.database):
    select_user = input("Wprowadz szukana fraze: ")
    users = db.find_users(select_user)
    for user in users:
        print(user)


def list_all(db: database.database):
    users = db.fetch_all('users')
    for user in users:
        print(user)


def login(db: database.database):
    name = input("Wprowadz imie: ")
    password = getpass("Wprowadź hasło: ")
    user = (db.find_users(name)).fetchone()

    if user[1] == name.lower() and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        print("Zalogowano")
        config.user_id = user[2]
        return True

    print("Błędne dane, spróbuj ponownie")
    return False


def register(db: database.database):
    name = input("Wprowadz imie: ")
    password = getpass("Wprowadź hasło: ")
    if db.check_user_name_exists(name) == 0:
        print("Nazwa już istnieje spróbuj jeszcze raz: ")
        return False
    if not re.fullmatch(r'[A-Za-z0-9]*$', name):
        print("Zły login- powinien składać sie tylko z liter i cyfr")
        return False
    if re.fullmatch(r'[A-Za-z0-9@#$%^&+=!?]{8,}', password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14)).decode('utf-8')
        db.add(name.lower(), hashed_password)
        print('Utworzono konto, możesz się zalogować')
        return True
    else:
        print(
            'Za słabe hasło - powinno składać się z 8 znaków w tym przynajmniej jedna mała i duża litera,'
            ' cyfra oraz znak specjalny'
        )
        return False


def run(db: database.database):
    global action
    print("Wybierz akcje: ")
    action = input("U - usunięcie użytkownika\nL - lista użytkowników\nS - znajdz uzytkownika\nP - menu pokoi\n")
    if action != "U" and action != "L" and action != 'S' and action != 'P':
        run(db)
    else:
        choice(action, db)


def choice(action, db):
    if action == 'U':
        delete_user(db)
        run(db)
    elif action == 'S':
        find_users(db)
        run(db)
    elif action == 'P':
        # RoomService.run()
        run(db)
    else:
        list_all(db)
        run(db)
