import database.database
import config
from getpass import getpass

import users.user_service
from database.rooms_database import Database


class RoomsService:
    def __init__(self):
        self.database = Database()

    def run(self):
        self.database.check_db_exists()
        print("Wybierz akcje: ")
        action = input("U - utwórz pokój\nL - lista pokoi\nD - dołącz do pokoju\nC - Usuń swój pokoj\nQ - wróć\n")

        if action != "U" and action != "L" and action != 'D' and action != 'C' and action != 'Q':
            self.run()
        else:
            self.choice(action)

    def choice(self, action):
        if action == 'U':
            self.make_room()
            self.run()
        elif action == 'L':
            self.list_room()
            self.run()
        elif action == 'D':
            self.join_room()
            self.run()
        elif action == 'Q':
            us = users.user_service.UserService()
            us.run()
        else:
            self.delete_room()
            self.run()

    def make_room(self):
        name = input("Wprowadz nazwę: ")
        password = getpass("Wprowadź hasło: ")
        self.database.make_room(name, password, config.user_id)

    def list_room(self):
        self.database.list_rooms()

    def join_room(self):
        print("Wybierz pokój do którego chcesz dołączyć: ")
        print("Lista: ")
        self.list_room()

        name = input("Wprowadź nazwę pokoju: ")
        password = getpass("Wprowadź hasło: ")
        self.database.join_room(name, password, config.user_id)

    def delete_room(self):
        print("Wybierz pokój który chcesz usunąć:  ")
        print("Lista: ")
        self.list_room()
        name = input("Wprowadź nazwę pokoju: ")
        self.database.delete_room(name)
