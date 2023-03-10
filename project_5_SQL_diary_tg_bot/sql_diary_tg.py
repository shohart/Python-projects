# Importing libraries
import sqlite3
import datetime as dt
from passlib.hash import bcrypt
import hashlib

from sqlite3 import Error
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Defining class


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        initial_tables = [
            """ CREATE TABLE IF NOT EXISTS entries (
                            id integer PRIMARY KEY,
                            tg_id text,
                            name text NOT NULL,
                            message_text text,
                            mood text,
                            timestamp,
                            UNIQUE(id, name, date)
                        ); """,
            """ CREATE TABLE IF NOT EXISTS users (
                            id integer PRIMARY KEY,
                            tg_id text,
                            name text NOT NULL,
                            birth_year text,
                            gender text,
                            email text,
                            password text,
                            registered,
                            last_login,
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

    def create_user(self, name, birth_year, email, password, tg_id, gender):

        hasher = bcrypt.using(rounds=13)
        password = hasher.hash(password)
        cur_date = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            sql = """
            INSERT INTO users (
                    name, birth_year, email, password,
                    tg_id, gender, registered, last_login
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?
                );"""
            conn = self.conn()
            cur = conn.cursor()
            cur.execute(
                sql,
                (name, birth_year, email, password, tg_id, gender, cur_date, cur_date),
            )
            conn.commit()
            conn.close()
        except Error as e:
            print(e)

    def create_entry(self, name, tg_id, message, password, mood):
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
        cur_date = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            sql = """ INSERT INTO entries
                      (name, tg_id, message_text, mood, timestamp)
                      VALUES (?, ?, ?, ?, ?);"""

            conn = self.conn()
            cur = conn.cursor()
            cur.execute(
                sql,
                (
                    name,
                    tg_id,
                    enc_message,
                    mood,
                    cur_date,
                ),
            )
            conn.commit()
            conn.close()
        except Error as e:
            print(e)

    def remove_user(self, username):
        try:
            sql1 = """
                DELETE FROM entries
                WHERE tg_id = ?;
            """
            sql2 = """
                DELETE FROM users
                WHERE tg_id = ?;
            """
            conn = self.conn()
            cur = conn.cursor()
            cur.execute(sql1, (username,))
            cur.execute(sql2, (username,))
            conn.commit()
            conn.close()
        except Error as e:
            print(e)

    def show_prev_entry(self, name, tg_id, password, limit=1, offset=0):

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
                SELECT date(timestamp), message_text, STRFTIME('%H:%M', timestamp), mood
                FROM entries
                WHERE tg_id = ?
                ORDER BY id DESC
                LIMIT ?
                OFFSET ?;"""
            cur.execute(sql, (tg_id, limit, offset))
            result = []
            data = cur.fetchall()
            for r in data:
                date, enc_message, msg_time, mood = r
                msg = fernet.decrypt(enc_message).decode("utf-8")
                result.append((date, msg, msg_time, mood))
            conn.close()

            return result

        except Error as e:
            print(e)

    def check_user(self, tg_id):
        try:
            sql = """SELECT * FROM users WHERE tg_id = ?;"""
            conn = self.conn()
            cur = conn.cursor()
            cur.execute(sql, (tg_id,))
            result = cur.fetchone()
            conn.close()
        except Error as e:
            print(e)

        # Return True if the input value was found, False otherwise
        return result is not None

    def check_password(self, tg_id, password):
        hasher = bcrypt.using(rounds=13)
        cur_date = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            sql = """SELECT password FROM
                     users WHERE tg_id = ?;
                     """
            conn = self.conn()
            cur = conn.cursor()
            cur.execute(sql, (tg_id,))
            result_to_verify = cur.fetchone()[0]
            conn.close()
        except Error as e:
            print(e)

        # Verify user and update last_login state
        verified = hasher.verify(password, result_to_verify)
        if verified:
            sql2 = """ UPDATE users SET last_login = ? WHERE tg_id = ? """
            conn = self.conn()
            cur = conn.cursor()
            cur.execute(sql2, (cur_date, tg_id))
            conn.commit()
            conn.close()

        # Return True if the input value was found, False otherwise
        return verified

    def get_password_hash(self, tg_id):
        try:
            sql = """SELECT password FROM
                     users WHERE tg_id = ?;
                     """
            conn = self.conn()
            cur = conn.cursor()
            cur.execute(sql, (tg_id,))
            pass_hash = cur.fetchone()[0]
            conn.close()
        except Error as e:
            print(e)

        # Return True if the input value was found, False otherwise
        return pass_hash

    def show_entries_range(self, name, tg_id, password, begin, end):

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
                    SELECT
                        date(timestamp),
                        message_text,
                        STRFTIME('%H:%M', timestamp),
                        mood
                    FROM entries
                    WHERE tg_id = ?
                    AND date BETWEEN ? AND ?
                    ORDER BY id DESC
                ;"""
            cur.execute(sql, (tg_id, begin, end))
            result = []
            data = cur.fetchall()
            for date, enc_message, msg_time, mood in data:
                msg = fernet.decrypt(enc_message).decode("utf-8")
                result.append((date, msg, msg_time, mood))
            conn.close()

            return result

        except Error as e:
            print(e)

    def get_user_bithdate(self, tg_id):
        try:
            conn = self.conn()
            cur = conn.cursor()

            sql = """
                    SELECT birth_year
                    FROM users
                    WHERE tg_id = ?
                ;"""
            cur.execute(sql, (tg_id,))
            data = cur.fetchone()[0]
            conn.close()

            return data

        except Error as e:
            print(e)
