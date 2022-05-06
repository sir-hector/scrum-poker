import database.database
from getpass import getpass
from users import rooms_service


class UserService:
    def __init__(self):
        self.database = database.database.Database('db.csv')
        self.RoomService = rooms_service.RoomsService()

    def delete_user(self):
        name = input("Podaj nazwe użytkownika do usunięcia: ")
        if self.database.check_user_name_exists(name) != 0:
            print("Nie ma w bazie takiego użytkownika, spróbuj ponownie")
            self.run()
        self.database.delete_user(name)

    def find_users(self):
        select_user = input("Wprowadz szukana fraze: ")
        self.database.find_users(select_user)

    def list_all(self):
        self.database.list_all()

    def login(self):
        name = input("Wprowadz imie: ")
        password = getpass("Wprowadź hasło: ")
        return self.database.login_user(name, password)

    def register(self):
        name = input("Wprowadz imie: ")
        password = getpass("Wprowadź hasło: ")
        return self.database.register_user(name, password)

    def run(self):
        global action
        print("Wybierz akcje: ")
        action = input("U - usunięcie użytkownika\nL - lista użytkowników\nS - znajdz uzytkownika\nP - menu pokoi\n")
        if action != "U" and action != "L" and action != 'S' and action != 'P':
            self.run()
        else:
            self.choice(action)

    def choice(self, action):
        if action == 'U':
            self.delete_user()
            self.run()
        elif action == 'S':
            self.find_users()
            self.run()
        elif action == 'P':
            self.RoomService.run()
        else:
            self.list_all()
            self.run()
