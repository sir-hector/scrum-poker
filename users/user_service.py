import re
from os import getenv
import bcrypt
import click
import config
import database.database
from getpass import getpass
import rooms
from rooms import rooms_service


@click.group()
def user():
    pass


@user.command('delete-user')
@click.option("--name", required=True)
@click.pass_obj
def delete_user(obj, name):
    db = obj['db']
    db.delete('users', name)


@user.command('find-user')
@click.option("--name", required=True)
@click.pass_obj
def find_users(obj, name):
    db = obj['db']
    users = db.find_users(name)
    for user in users:
        print(user)


@user.command('find-all')
@click.pass_obj
def list_all(obj):
    db = obj['db']
    users = db.fetch_all('users')
    for user in users:
        print(user)


@user.group('login')
@click.option("--name", required=True)
@click.password_option(confirmation_prompt=False)
@click.pass_obj
def login(obj, name, password):
    db = database.database.get_database(getenv('DB_NAME'))
    obj['db'] = db
    user = (db.find_users(name)).fetchone()

    if user[1] == name.lower() and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        print("Zalogowano")
        config.user_id = user[0]
        return True

    print("Błędne dane, spróbuj ponownie")
    return False


login.add_command(rooms.rooms_service.room)


@user.command()
@click.option("--name", required=True)
@click.password_option()
@click.pass_obj
def register(obj, name, password):
    db = database.database.get_database(getenv('DB_NAME'))
    obj['db'] = db
    if db.check_name_exists('users', name) == 0:
        print("Nazwa już istnieje spróbuj jeszcze raz: ")
        return False
    if not re.fullmatch(r'[A-Za-z0-9]*$', name):
        print("Zły login- powinien składać sie tylko z liter i cyfr")
        return False
    if re.fullmatch(r'[A-Za-z0-9@#$%^&+=!?]{8,}', password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14)).decode('utf-8')
        db.add('users', name.lower(), hashed_password)
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
        rooms_service.run(db)
        run(db)
    else:
        list_all(db)
        run(db)


def validate_login(login):
    if not re.fullmatch(r'[A-Za-z0-9]*$', login):
        return False
    return True


def validate_password(password):
    if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=!?]{8,}', password):
        return False
    return True


def has_user(db, name):
    if db.check_name_exists('users', name):
        return False
    return True


def create_user(db, name, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14)).decode('utf-8')
    db.add('users', name.lower(), hashed_password)


def login_user(db, name, password):
    user = (db.find_users(name)).fetchone()
    if user and user[1] == name.lower() and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        return user[0]

    return False
