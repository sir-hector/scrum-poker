import sys
import os
from dotenv import load_dotenv
import sqlite3
load_dotenv()


class Database:
    def __init__(self, database_name):
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def init(self):
        return self

    def check_name_exists(self, table, username):
        find_users = self.fetch_all_with_conditions(table, name=username)
        if len(find_users.fetchall()) > 0:
            return True

    def delete(self, table, name):
        sql = f"DELETE FROM {table} WHERE name=?"
        self.cursor.execute(sql, (name,))
        self.connection.commit()

    def delete2(self, table, name):
        sql = f"DELETE FROM {table} WHERE roomId=?"
        self.cursor.execute(sql, (name,))
        self.connection.commit()

    def deleteTopic(self, table, name):
        sql = f"DELETE FROM {table} WHERE topic=?"
        self.cursor.execute(sql, (name,))
        self.connection.commit()

    def deleteVotes(self, table, name):
        sql = f"DELETE FROM {table} WHERE topicId=?"
        self.cursor.execute(sql, (name,))
        self.connection.commit()

    def update(self,  name, roomId):
        sql = f"UPDATE rooms set topic = '{name}' where id = {roomId}"
        print(sql)
        self.cursor.execute(sql)
        self.connection.commit()

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

    def add(self, table, name, password):
        print('Dodaje do bazy danych')
        self.insert(table, None, name, password)

    def index(self, category):
        print('Lista uzytkownikow')
        links = self.fetch_all_with_conditions('users', name=category)
        for link in links:
            print(link)



def get_database(path):
    db = Database(path)
    db.init()
    return db


def initialize_db(db):
    db.create_table('''CREATE TABLE users
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT)''')
    db.create_table('''CREATE TABLE rooms
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT, ownerID INTEGER, topic TEXT)''')
    db.create_table('''CREATE TABLE rooms_members
                (roomId INTEGER , ownerId INTEGER)''')
    db.create_table('''CREATE TABLE room_topics
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, roomId INTEGER , topic TEXT, status BOOLEAN)''')
    db.create_table('''CREATE TABLE rooms_votes
                (id INTEGER PRIMARY KEY AUTOINCREMENT, value TEXT, userID INTEGER, topicId INTEGER)''')




