import sys
import csv
import os
import bcrypt
import re
import config
from getpass import getpass


class Database:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.db_path = os.path.join(self.current_dir, 'rooms.csv')
        self.db_path_members = os.path.join(self.current_dir, 'rooms_members.csv')

    def check_db_exists(self):
        try:
            os.stat(self.db_path)
            os.stat(self.db_path_members)
        except FileNotFoundError:
            f = open(self.db_path, "w")
            f.close()
            f = open(self.db_path_members, "w")
            f.close()

    def check_room_exists(self, id):
        with open(self.db_path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if id.lower() == row[0].lower():
                    return 0

    def make_room(self, name, password, user_id):
        if self.check_room_exists(name) == 0:
            print("Nazwa już istnieje spróbuj jeszcze raz: ")
            return False
        if not re.fullmatch(r'[A-Za-z0-9]*$', name):
            print("Zła nazwa- powinien składać sie tylko z liter i cyfr")
            return False
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=!?]{8,}', password):
            lines = list()
            with open(self.db_path, 'a', newline='') as file:
                csv_writer = csv.writer(file)
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14)).decode('utf-8')
                csv_writer.writerow([name.lower(), hashed_password, user_id])
                print('Utworzono pokój')
            return True
        else:
            print(
                'Za słabe hasło - powinno składać się z 8 znaków w tym przynajmniej jedna mała i duża litera,'
                ' cyfra oraz znak specjalny'
            )
            return False

    def list_rooms(self):
        with open(self.db_path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                print("Nazwa pokoju: " + row[0] + " id: " + row[2])

    def join_room(self, name, password, user_id):
        with open(self.db_path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            if self.check_users_in_rooms(name, user_id) == 0:
                print("już należysz do tego pokoju")
                return False
            for row in csv_reader:
                if row[0] == name.lower() and bcrypt.checkpw(password.encode('utf-8'), row[1].encode('utf-8')):
                    print("Dolaczono do pokoju: " + name)
                    self.rooms_members(name, config.user_id)
                    return True
        print("Błędne dane, spróbuj ponownie")
        return False

    def delete_room(self, name):
        lines = list()
        with open(self.db_path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                lines.append(row)
                if name == row[0] and config.user_id != row[2]:
                    print("nie mozna usunąć czyjegoś pokoju")
                    return
                elif name == row[0] and config.user_id == row[2]:
                    print("Mozemy usunąć twój pokoj")
                    password = getpass("Wprowadź hasło: ")
                    if bcrypt.checkpw(password.encode('utf-8'), row[1].encode('utf-8')):
                        print("Usuwanie zakończone sukcesem")
                        lines.remove(row)
                        self.delete_rooms_members(name)
                    else:
                        print("błędne hasło")
                        return

        with open(self.db_path, 'w', newline='') as writeFile:
            csv_writer = csv.writer(writeFile)
            for row in lines:
                csv_writer.writerow(row)
        return 0

    def rooms_members(self, name, user_id):
        with open(self.db_path_members, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow([name.lower(), user_id])

    def delete_rooms_members(self, name):
        lines = list()
        with open(self.db_path_members, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                lines.append(row)
                for field in row:
                    if field == name:
                        lines.remove(row)
        with open(self.db_path_members, 'w', newline='') as writeFile:
            csv_writer = csv.writer(writeFile)
            for row in lines:
                csv_writer.writerow(row)
        return 0

    def check_users_in_rooms(self, id, name):
        with open(self.db_path_members, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if id == row[0] and name == row[1]:
                    return 0

