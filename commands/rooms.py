from rooms import rooms_service
from rooms.exceptions import RoomExist, RoomException


def list_all(user_id):
    return rooms_service.get_all_rooms(user_id)


def create_room(db, name, password, userId):
    if not rooms_service.validate_name(db, name):
        raise RoomExist("Existing Room")

    if not rooms_service.validate_password(password):
        raise RoomException("wrong_credentials")

    rooms_service.create_room(db, name, password, userId)


def join_room(db, room_id, password, userId):
    if not rooms_service.find_room_by_id(db, room_id):
        raise RoomExist("Room does not exist")

    if rooms_service.check_if_room_has_user(db, room_id, userId):
        raise RoomException("Already belong")

    if not rooms_service.room_join(db, room_id, password, userId):
        raise RoomException("Wrong Password")


def get_room_details(db, room_id, userId):
    room = rooms_service.find_room_by_id(db, room_id)
    if not room:
        raise RoomExist("Room does not exist")

    if not rooms_service.check_if_room_has_user(db, room_id, userId):
        raise RoomException("Tou are not member of this room")
    return room


def change_room_topic(db, room_id, user_id, topic, password):
    room = rooms_service.find_room_by_id(db, room_id)
    if not room:
        raise RoomExist("Room does not exist")
    if not rooms_service.check_if_is_owner(db, room_id, user_id):
        raise RoomException("Tou are not member of this room")
    if not rooms_service.update_topic(db, room_id, user_id, topic):
        raise RoomException("Cant Change room Topuc")
    return rooms_service.find_room_by_id(db, room_id)


def get_all_votes(db, user_id, room_id):
    room = rooms_service.find_room_by_id(db, room_id)
    if not room:
        raise RoomExist("Room does not exist")

    if not rooms_service.check_if_room_has_user(db, room_id, user_id):
        raise RoomException("Tou are not member of this room")

    if not rooms_service.check_if_room_has_topic(db, room_id):
        raise RoomException("Room does not have topic")

    return rooms_service.get_all_votes(db, room_id)


def put_vote(db, user_id, room_id, vote):
    room = rooms_service.find_room_by_id(db, room_id)
    correctValues = [0, 0.5, 1, 2, 3, 5, 8, 13, 20, 50, 100, 200, -1, -2]
    if not (vote in correctValues):
        raise RoomException("Wrong Vote")
    if not room:
        raise RoomExist("Room does not exist")
    if not rooms_service.check_if_room_has_user(db, room_id, user_id):
        raise RoomException("Tou are not member of this room")

    if not rooms_service.check_if_room_has_topic(db, room_id):
        raise RoomException("Room does not have topic")

    rooms_service.put_votes(db, room_id, user_id, vote)
