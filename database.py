import sqlite3
from cryptography.fernet import Fernet

class Database:
    def __init__(self, db_name='users.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT
                )
            ''')

    def add_user(self, username, password):
        encrypted_password = self.cipher.encrypt(password.encode())
        with self.conn:
            self.conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                             (username, encrypted_password))

    def verify_user(self, username, password):
        cursor = self.conn.execute('SELECT password FROM users WHERE username = ?',
                                    (username,))
        row = cursor.fetchone()
        if row:
            decrypted_password = self.cipher.decrypt(row[0]).decode()
            return decrypted_password == password
        return False

    def close(self):
        self.conn.close()