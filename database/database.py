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
        find_users = self.fetch_all_with_conditions('users', name=username)
        if len(find_users.fetchall()) > 0:
            return 0

    def delete(self, table, name):
        sql = f"DELETE FROM {table} WHERE name=?"
        self.cursor.execute(sql, (name,))
        self.connection.commit()

    def check_db_exists(self):
        try:
            os.stat(self.db_path)
        except FileNotFoundError:
            f = open(self.db_path, "w")
            f.close()

    def find_users(self, select_user):
        find_users = self.fetch_all_with_conditions('users', name=select_user)
        return find_users


    def create_table(self, sql: str):
        self.cursor.execute(sql)
        self.connection.commit()

    def insert(self, table, *values):
        self.cursor.execute(f"INSERT INTO {table} VALUES ({','.join(['?' for _ in values])})", values)
        self.connection.commit()

    def fetch_all_with_conditions(self, table, **conditions):
        return self.cursor.execute(
            f"SELECT * FROM {table} WHERE {' and '.join([f'{condition}=?' for condition in conditions])}",
            (*conditions.values(),)
        )

    def fetch_all(self, table):
        return self.cursor.execute(f"SELECT name FROM {table}")

    def add(self, name, password):
        print('Dodaje do bazy danych')
        self.insert('users', None, name, password)

    def index(self, category):
        print('Lista uzytkownikow')
        links = self.fetch_all_with_conditions('users', name=category)
        for link in links:
            print(link)


def get_database(path):
    db = Database(path)
    db.init()
    return db

# @click.group()
# def cli():
#     pass


# @click.command()
# def setup():
#     print('Tworzenie Tabeli w bazie danych')
#     db = Database(getenv('DB_NAME'))
#     db.create_table('''CREATE TABLE users
#         (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT)''')


# @click.command()
# @click.argument('name')
# @click.argument('password')
# def add(name, password):
#     print('Dodaje do bazy danych')
#     db = Database(getenv('DB_NAME'))
#     db.insert('users', None, name, password)


# @click.command()
# @click.argument('category')
# def index(category):
#     print('Lista uzytkownikow')
#     db = Database(getenv('DB_NAME'))
#     links = db.fetch_all('users', name=category)
#     for link in links:
#         print(link)


# cli.add_command(setup)
# cli.add_command(add)
# cli.add_command(index)
