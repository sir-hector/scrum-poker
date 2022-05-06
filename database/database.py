import sys
import csv
import os
import bcrypt
import re
import config
from os import getenv
from dotenv import load_dotenv
import sqlite3
import click

load_dotenv()


class Database:
    def __init__(self, database_name):
        self.current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.db_path = os.path.join(self.current_dir, 'db.csv')
        # self.db_path = os.path.join(self.current_dir, db_path)
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def init(self):
        return self

    def check_user_name_exists(self, username):
        with open(self.db_path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if username.lower() == row[0].lower():
                    return 0

    def delete_user(self, name):
        lines = list()
        with open(self.db_path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                lines.append(row)
                for field in row:
                    if field == name:
                        lines.remove(row)
        with open(self.db_path, 'w', newline='') as writeFile:
            csv_writer = csv.writer(writeFile)
            for row in lines:
                csv_writer.writerow(row)
        return 0

    def check_db_exists(self):
        try:
            os.stat(self.db_path)
        except FileNotFoundError:
            f = open(self.db_path, "w")
            f.close()

    def register_user(self, username, password):
        if self.check_user_name_exists(username) == 0:
            print("Nazwa już istnieje spróbuj jeszcze raz: ")
            return False
        if not re.fullmatch(r'[A-Za-z0-9]*$', username):
            print("Zły login- powinien składać sie tylko z liter i cyfr")
            return False
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=!?]{8,}', password):
            lines = list()
            with open(self.db_path, 'r+', newline='') as file:
                csv_writer = csv.writer(file)
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    lines.append(row)
                if lines:
                    newId = int(lines[-1][2]) + 1
                else:
                    newId = 1
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14)).decode('utf-8')
                csv_writer.writerow([username.lower(), hashed_password, newId])
                print('Utworzono konto, możesz się zalogować')
            return True
        else:
            print(
                'Za słabe hasło - powinno składać się z 8 znaków w tym przynajmniej jedna mała i duża litera,'
                ' cyfra oraz znak specjalny'
            )
            return False

    def login_user(self, username, password):
        with open(self.db_path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row[0] == username.lower() and bcrypt.checkpw(password.encode('utf-8'), row[1].encode('utf-8')):
                    print("Zalogowano")
                    config.user_id = row[2]
                    return True
        print("Błędne dane, spróbuj ponownie")
        return False

    def find_users(self, select_user):
        with open(self.db_path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if select_user in row[0]:
                    print(row[0])

    def list_all(self):
        with open(self.db_path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                print(row[0])

    def create_table(self, sql: str):
        self.cursor.execute(sql)
        self.connection.commit()

    def insert(self, table, *values):
        self.cursor.execute(f"INSERT INTO {table} VALUES ({','.join(['?' for _ in values])})", values)
        self.connection.commit()

    def fetch_all(self, table, **conditions):
        return self.cursor.execute(
            f"SELECT * FROM {table} WHERE {' and '.join([f'{condition}=?' for condition in conditions])}",
            (*conditions.values(),)
        )


def get_database(path):
    db = Database(path)
    db.init()
    return db


@click.group()
def cli():
    pass


@click.command()
def setup():
    print('Tworzenie Tabeli w bazie danych')
    db = Database(getenv('DB_NAME'))
    db.create_table('''CREATE TABLE users
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT)''')


@click.command()
@click.argument('name')
@click.argument('password')
def add(name, password):
    print('Dodaje do bazy danych')
    db = Database(getenv('DB_NAME'))
    db.insert('users', None, name, password)


@click.command()
@click.argument('category')
def index(category):
    print('Lista uzytkownikow')
    db = Database(getenv('DB_NAME'))
    links = db.fetch_all('users', name=category)
    for link in links:
        print(link)


cli.add_command(setup)
cli.add_command(add)
cli.add_command(index)
