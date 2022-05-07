import re
import bcrypt
import click
import database.database
import config
from getpass import getpass
import users


@click.group()
def room():
    pass


def run(db: database.database):
    print("Wybierz akcje: ")
    action = input("U - utwórz pokój\nL - lista pokoi\nD - dołącz do pokoju\nC - Usuń swój pokoj\nQ - wróć\n")

    if action != "U" and action != "L" and action != 'D' and action != 'C' and action != 'Q':
        run(db)
    else:
        choice(db, action)


def choice(db, action):
    if action == 'U':
        name = input("Wprowadz nazwę: ")
        password = getpass("Wprowadź hasło: ")
        make_room(db, name, password)
        run(db)
    elif action == 'L':
        list_room(db)
        run(db)
    elif action == 'D':
        name = input("Wprowadź nazwę pokoju: ")
        password = getpass("Wprowadź hasło: ")
        join_room(db, name, password)
        run(db)
    elif action == 'Q':
        us = users.user_service.run(db)
        us.run()
    else:
        delete_room(db)
        run(db)


@room.command()
@click.option("--name", required=True)
@click.password_option()
@click.pass_obj
def make_room(obj, name, password):
    db = obj['db']
    if db.check_name_exists('rooms', name) == 0:
        print("Nazwa już istnieje spróbuj jeszcze raz: ")
        return False
    if not re.fullmatch(r'[A-Za-z0-9]*$', name):
        print("Zła nazwa- powinien składać sie tylko z liter i cyfr")
        return False
    if re.fullmatch(r'[A-Za-z0-9@#$%^&+=!?]{8,}', password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14)).decode('utf-8')
        db.insert('rooms', None, name.lower(), hashed_password, config.user_id)
        print('Utworzono pokój')
        return True
    else:
        print(
            'Za słabe hasło - powinno składać się z 8 znaków w tym przynajmniej jedna mała i duża litera,'
            ' cyfra oraz znak specjalny'
        )
        return False


@room.command()
@click.pass_obj
def list_room(obj):
    db = obj['db']
    rooms = db.fetch_all('rooms')
    for room in rooms:
        print(room)


@room.command()
@click.option("--name", required=True)
@click.password_option()
@click.pass_obj
def join_room(obj, name ,password):
    db = obj['db']

    if (db.check_name_exists('rooms', name) is None):
        print("Nie ma takiego pokoju: ")
        return False
    room = db.fetch_all_with_conditions('rooms', name=name).fetchone()

    if len(db.fetch_all_with_conditions('rooms_members', roomId=room[0], ownerId=config.user_id).fetchall()) > 0:
        print("już należysz do tego pokoju")
        return False

    if room[1] == name.lower() and bcrypt.checkpw(password.encode('utf-8'), room[2].encode('utf-8')):
        print("Dolaczono do pokoju: " + name)
        db.insert('rooms_members', room[0], config.user_id)
        return True
    print("Błędne dane, spróbuj ponownie")
    return False


@room.command()
@click.option("--name", required=True)
@click.password_option()
@click.pass_obj
def delete_room(obj, name, password):
    db = obj['db']

    if db.check_name_exists('rooms', name) is None:
        print("Nie ma takiego pokoju: ")
        return False
    room = db.fetch_all_with_conditions('rooms', name=name).fetchone()
    print(room)

    if config.user_id != room[3]:
        print("nie mozna usunąć czyjegoś pokoju")
        return False
    else:
        if bcrypt.checkpw(password.encode('utf-8'), room[2].encode('utf-8')):
            db.delete('rooms', room[1])
            db.delete2('rooms_members', room[0])
            print("Usuwanie zakończone sukcesem")
        else:
            print("błędne hasło")
            return False
    return

@room.command()
@click.option("--name", required=True)
@click.option("--topic", required=True)
@click.pass_obj
def create_topic(obj, name, topic):
    pass
