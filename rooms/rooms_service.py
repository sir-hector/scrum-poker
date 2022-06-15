import json
import re
from typing import List

import bcrypt
import click
import database.database
import config
from getpass import getpass
import users
from database.room_model import Room
from database.users_model import User
from database.vote_model import Vote, Votes


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
        db.insert('rooms', None, name.lower(), hashed_password, config.user_id, "")
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
@click.password_option(confirmation_prompt=False)
@click.pass_obj
def join_room(obj, name, password):
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
@click.password_option(confirmation_prompt=False)
@click.pass_obj
def delete_room(obj, name, password):
    db = obj['db']

    if db.check_name_exists('rooms', name) is None:
        print("Nie ma takiego pokoju: ")
        return False
    room = db.fetch_all_with_conditions('rooms', name=name).fetchone()

    if config.user_id != room[3]:
        print("nie mozna usunąć czyjegoś pokoju")
        return False
    else:
        if bcrypt.checkpw(password.encode('utf-8'), room[2].encode('utf-8')):
            db.delete('rooms', room[1])
            db.deleteMembers('rooms_members', room[0])
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
    db = obj['db']
    if db.check_name_exists('rooms', name) is None:
        print("Nie ma takiego pokoju: ")
        return False
    room = db.fetch_all_with_conditions('rooms', name=name).fetchone()
    if config.user_id != room[3]:
        print("nie mozna ustawic tematu nie swoim pokoju")
        return False
    roomsTopics = db.fetch_all_with_conditions('room_topics', roomId=room[0], status=0).fetchone()
    if roomsTopics:
        print("Pokój ma aktywny temat")
        return False
    print('Dodano temat')
    db.insert('room_topics', None, room[0], topic, 0)
    return True


@room.command()
@click.option("--name", required=True)
@click.option("--topic", required=True)
@click.pass_obj
def delete_topic(obj, name, topic):
    db = obj['db']
    if db.check_name_exists('rooms', name) is None:
        print("Nie ma takiego pokoju: ")
        return False
    room = db.fetch_all_with_conditions('rooms', name=name).fetchone()
    if config.user_id != room[3]:
        print("nie mozna zmieniać tematu w nie swoim pokoju")
        return False
    roomsTopics = db.fetch_all_with_conditions('room_topics', topic=topic).fetchone()
    if roomsTopics is None:
        print("Nie ma takiego tematu")
        return False
    print('Usunieto temat')
    db.deleteVotes('rooms_votes', roomsTopics[0])
    db.deleteTopic('room_topics', topic)
    return True


@room.command()
@click.option("--topic-id", required=True)
@click.option("--value", required=True,
              type=click.Choice(['0', '0.5', '1', '2', '3', '5', '8', '13', '20', '50', '100', '200', '-1', '-2']))
@click.pass_obj
def rate_topic(obj, topic_id, value):
    db = obj['db']
    topic = db.fetch_all_with_conditions('room_topics', id=topic_id).fetchone()

    if topic is None:
        print("Topic is invalid")
        return

    roomId = topic[1]
    roomVoted = db.fetch_all_with_conditions('rooms', id=roomId).fetchone()
    if config.user_id != roomVoted[3]:
        print("You are not in this room")
        return False

    db.insert('rooms_votes', None, value, config.user_id, topic_id)
    print("Dodano głos")


def get_all_rooms(db, user_id) -> List[Room]:
    rooms = db.fetch_all_with_conditions('rooms_members', ownerId=user_id)
    print(rooms)
    return [Room(name=room[1], id=room[0], owner=room[1]) for room in rooms]


def validate_name(db, name):
    return db.check_name_exists('rooms', name)


def validate_password(password):
    if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=!?]{8,}', password):
        return False
    return True


def create_room(db, name, password, userId):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14)).decode('utf-8')
    db.insert('rooms', None, name.lower(), hashed_password, userId, "")
    return True


def find_room_by_id(db, id):
    room = db.fetch_all_with_conditions('rooms', id=id).fetchone()
    if not room:
        return False
    rooms_members = db.fetch_all_with_conditions('rooms_members', roomId=id).fetchall()
    members = [User(username=user[0]) for user in rooms_members]
    return Room(id=room[0], name=room[1], owner=room[3], users=members)


def check_if_room_has_user(db, room_id, userId):
    rooms_members = db.fetch_all_with_conditions('rooms_members', roomId=room_id, ownerId=userId).fetchone()
    if rooms_members is None:
        return False
    return True


def room_join(db, room_id, password, user_id):
    room = db.fetch_all_with_conditions('rooms', id=room_id).fetchone()
    if bcrypt.checkpw(password.encode('utf-8'), room[2].encode('utf-8')):
        db.insert('rooms_members', room_id, user_id)
        return True
    return False


def check_if_is_owner(db, room_id, userId):
    room = db.fetch_all_with_conditions('rooms', id=room_id).fetchone()
    if userId == room[3]:
        return True
    return False


def check_if_room_has_topic(db, room_id):
    room_topic = db.fetch_all_with_conditions('room_topics', roomId=room_id).fetchone()
    if room_topic is None:
        return False
    return True


def update_topic(db, room_id, user_id, topic):
    db.deleteRoomTopic('room_topics', room_id=room_id)
    db.insert('room_topics', None, room_id, topic, 0)
    room = db.fetch_all_with_conditions('rooms', id=room_id).fetchone()
    rooms_members = db.fetch_all_with_conditions('rooms_members', roomId=room_id).fetchall()
    members = [User(username=user[0]) for user in rooms_members]
    return Room(id=room[0], name=room[1], owner=room[3], members=members)


def get_all_votes(db, room_id):
    room_topic = db.fetch_all_with_conditions('room_topics', roomId=room_id).fetchone()
    topic_ud = room_topic[0]
    votes = db.fetch_all_votes('rooms_votes', topic_ud)
    votes = [Vote(username=vote[1], value=float(vote[0])) for vote in votes]
    return Votes(votes=votes)


def get_user_votes(db, room_id, user_id):
    room_topic = db.fetch_all_with_conditions('room_topics', roomId=room_id).fetchone()
    topic_ud = room_topic[0]
    votes = db.fetch_all_with_conditions('rooms_votes', userID=user_id, topicId=topic_ud).fetchone()
    if votes is None:
        return False
    return True


def put_votes(db, value, userID, room_id, condition):
    room_topic = db.fetch_all_with_conditions('room_topics', roomId=room_id).fetchone()
    topic_id = room_topic[0]
    if not condition:
        db.insert('rooms_votes', None, value, userID, topic_id)
    db.update_vote(value, topic_id)

