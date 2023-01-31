# Importing libraries
import sqlite3
import datetime as dt
from passlib.hash import bcrypt
import hashlib

from sqlite3 import Error
from getpass import getpass

import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


db_name = "sql_diary.db"

# Defining functions


def initial_choice(username, password):

    while True:
        if db:
            choice = input(
                '\nMake a selection:\n"add" = new entry,\n"view" = previous entry.\n'
            )

            if choice.strip().lower() not in ["add", "view"]:
                print("Wrong input!")
                continue

            elif choice.strip().lower() == "add":
                entry = input("Write new entry: ")
                db.create_entry(username, entry, password)
                break

            elif choice.lower() == "view":
                show_entry = True
                offset = 0
                while show_entry:
                    try:
                        show_next = "_"
                        entry = db.show_prev_entry(username, password, offset)
                        date = entry[2]
                        print("\ndate: ", date)
                        print("\nmessage: ", entry[3], "\n")

                        while show_next.capitalize()[0] not in ["Y", "N"]:
                            show_next = input(
                                "\nShow previous entry? Enter Yes or No: \n"
                            )

                            if show_next.capitalize()[0] not in ["Y", "N"]:
                                # print("\n" * 100)
                                print(
                                    "\nSorry, I didn't understand.\n"
                                    "Please make sure to enter Yes or No."
                                )
                    except IndexError:

                        show_next = "N"

                    show_entry = bool(show_next.capitalize()[0] == "Y")
                    offset += 1
                    break
        else:
            print("I couldnt allocate database file")
            pass


def end_choice():

    go = "_"

    try:

        while go.capitalize()[0] not in ["Y", "N"]:
            go = input("Anything else? Enter Yes or No: ")

            if go.capitalize()[0] not in ["Y", "N"]:
                # print("\n" * 100)
                print(
                    "Sorry, I didn't understand.\n"
                    "Please make sure to enter Yes or No."
                )
    except IndexError:

        go = "N"

    return bool(go.capitalize()[0] == "Y")


# Defining classes


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        initial_tables = [
            """ CREATE TABLE IF NOT EXISTS entries (
                            id integer PRIMARY KEY,
                            name text NOT NULL,
                            date text,
                            message_text text,
                            UNIQUE(id, name, date)
                        ); """,
            """ CREATE TABLE IF NOT EXISTS users (
                            id integer PRIMARY KEY,
                            name text NOT NULL,
                            birth_year text,
                            email text,
                            password text,
                            UNIQUE(id, name, email)
                        ); """,
        ]
        for table in initial_tables:
            self.create_table(table)

    def conn(self):
        try:
            return sqlite3.connect(self.db_name)
        except Error as e:
            print(e)

    def create_table(self, new_table):
        try:
            conn = self.conn()
            cur = conn.cursor()
            cur.execute(new_table)
            conn.commit()
            conn.close()
        except Error as e:
            print(e)

    def create_user(self, name, birth_year, email, password):

        hasher = bcrypt.using(rounds=13)
        password = hasher.hash(password)

        try:
            sql = """ INSERT INTO users
                      (name, birth_year, email, password)
                      VALUES (?, ?, ?, ?);"""
            conn = self.conn()
            cur = conn.cursor()
            cur.execute(sql, (name, birth_year, email, password))
            conn.commit()
            conn.close()
        except Error as e:
            print(e)

    def create_entry(self, name, message, password):
        password = bytes(password, encoding="utf-8")
        salt = hashlib.sha256(name.encode()).digest()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        fernet = Fernet(key)
        enc_message = fernet.encrypt(bytes(message, encoding="utf-8"))

        try:
            sql = """ INSERT INTO entries
                      (name, date, message_text)
                      VALUES (?, ?, ?);"""
            conn = self.conn()
            cur = conn.cursor()
            cur.execute(
                sql,
                (name, dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), enc_message),
            )
            conn.commit()
            conn.close()
        except Error as e:
            print(e)

    def show_prev_entry(self, name, password, offset=0):

        password = bytes(password, encoding="utf-8")
        salt = hashlib.sha256(name.encode()).digest()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))

        fernet = Fernet(key)
        try:
            conn = self.conn()
            cur = conn.cursor()

            sql = """
                SELECT * FROM entries
                WHERE name=?
                ORDER BY id DESC
                LIMIT 1
                OFFSET ?;"""
            cur.execute(sql, (name, offset))
            id, name, date, enc_message = cur.fetchone()
            conn.close()
            message = fernet.decrypt(enc_message).decode("utf-8")

            return id, name, date, message

        except Error as e:
            print(e)

    def check_user(self, name):
        try:
            sql = """SELECT * FROM users WHERE name = ?;"""
            conn = self.conn()
            cur = conn.cursor()
            cur.execute(sql, (name,))
            result = cur.fetchone()
            conn.close()
        except Error as e:
            print(e)

        # Return True if the input value was found, False otherwise
        return result is not None

    def check_password(self, name, password):
        hasher = bcrypt.using(rounds=13)
        try:
            sql = """SELECT * FROM
                     users WHERE name = ?;
                     """
            conn = self.conn()
            cur = conn.cursor()
            cur.execute(sql, (name,))
            result_to_verify = cur.fetchone()[4]
            conn.close()
        except Error as e:
            print(e)

        # Return True if the input value was found, False otherwise
        return hasher.verify(password, result_to_verify)


db = Database(db_name)

if __name__ == "__main__":

    diary_start = True

    while diary_start:

        # Get creditials
        username = input("Username? ")
        print(f"Hello, {username}!")

        while True:

            if db.check_user(username):
                password = getpass("Password?: ")
                if db.check_password(username, password):
                    initial_choice(username, password)
                    break
                else:
                    print("Wrong password! Try again!")
                    continue

            else:
                print("\nSeems that you new here! Let's get you set up!")
                birth_year = input("Enter your year of birth: ")
                password = getpass("Password?: ")
                email = input("Enter your email: ")
                db.create_user(username, birth_year, email, password)
                continue

        diary_start = end_choice()
