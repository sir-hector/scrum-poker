import json
import re
from typing import List

import bcrypt
import click
from sqlalchemy import and_

import database.database
import config
from getpass import getpass
import users
from database.room_model import Room
from database.sql import SessionLocal, engine, association_table, RoomVotes
from database.users_model import User
from database.vote_model import Vote, Votes
from database.sql import Room as Room2
from database.sql import User as User2
from database.sql import RoomTopic as RoomTopic


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


def get_all_rooms(user_id) -> List[Room]:
    local_session = SessionLocal(bind=engine)
    user = local_session.query(User2) \
        .filter(User2.id == user_id) \
        .first()
    rooms = user.rooms
    return [Room(name=room.name, id=room.id, owner=room.owner.name) for room in rooms]


def validate_name(db, name):
    local_session = SessionLocal(bind=engine)
    room = local_session.query(Room2).filter(Room2.name == name).first()
    if room:
        return False
    return True


def validate_password(password):
    if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=!?]{8,}', password):
        return False
    return True


def create_room(db, name, password, userId):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14)).decode('utf-8')
    local_session = SessionLocal(bind=engine)
    new_room = Room2(name=name, password=hashed_password, ownerId=userId)
    local_session.add(new_room)
    local_session.commit()


def find_room_by_id(db, id):
    local_session = SessionLocal(bind=engine)
    room = local_session.query(Room2).filter(Room2.id == id).first()

    if not room:
        return False
    members = [User(username=user.name) for user in room.users]

    return Room(id=room.id, name=room.name, owner=room.owner.id, users=members)


def check_if_room_has_user(db, room_id, userId):
    local_session = SessionLocal(bind=engine)
    query_rooms_member = local_session.query(association_table).filter(association_table.c.user_id == userId) \
        .filter(association_table.c.room_id == room_id).first()
    if query_rooms_member is None:
        return False
    return True


def room_join(db, room_id, password, user_id):
    local_session = SessionLocal(bind=engine)
    room = local_session.query(Room2).filter(Room2.id == room_id).first()
    user = local_session.query(User2).filter(User2.id == user_id).first()
    if bcrypt.checkpw(password.encode('utf-8'), room.password.encode('utf-8')):
        room.users.append(user)
        local_session.commit()
        return True
    return False


def check_if_is_owner(db, room_id, userId):
    local_session = SessionLocal(bind=engine)
    room = local_session.query(Room2).filter(Room2.id == room_id).filter(Room2.ownerId == userId).first()
    if room:
        return True
    return False


def check_if_room_has_topic(db, room_id):
    local_session = SessionLocal(bind=engine)
    room_topic = local_session.query(RoomTopic).where(RoomTopic.roomId == room_id).first()
    if room_topic is None:
        return False
    return True


def update_topic(db, room_id, user_id, topic):
    local_session = SessionLocal(bind=engine)
    room_topic = local_session.query(RoomTopic).where(RoomTopic.roomId == room_id).first()

    if room_topic:
        local_session.query(RoomVotes).filter_by(topicId=room_topic.id).delete()
        local_session.delete(room_topic)
        local_session.commit()

    new_topic = RoomTopic(topic=topic, roomId=room_id, status=0)
    local_session.add(new_topic)
    local_session.commit()

    return True


def get_all_votes(db, room_id):
    local_session = SessionLocal(bind=engine)
    votes = local_session.query(RoomVotes) \
        .join(User2) \
        .join(RoomTopic) \
        .filter(RoomTopic.roomId == room_id) \
        .all()

    result = [Vote(username=vote.users.name, value=float(vote.value)) for vote in votes]
    return Votes(votes=result)


def put_votes(db, room_id, user_id, value):
    local_session = SessionLocal(bind=engine)
    UserVote = local_session.query(RoomVotes) \
        .join(User2) \
        .join(RoomTopic) \
        .filter(User2.id == user_id) \
        .filter(RoomTopic.roomId == room_id) \
        .first()
    print(UserVote)
    if UserVote is not None:
        UserVote.value = value
        local_session.add(UserVote)
        local_session.commit()
    else:
        topicId = local_session.query(RoomTopic).filter(RoomTopic.roomId == room_id).first()
        newVote = RoomVotes(value=value, topicId=topicId.id, userId=user_id)
        local_session.add(newVote)
        local_session.commit()
