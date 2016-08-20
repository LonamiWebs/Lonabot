import sqlite3
from tg_objects.user import User


class Database:
    """
    Represents a database, which keeps track of stuff such as users, sent files, etc.
    """

    def __init__(self):
        # Start a connection with the database
        self.connection = sqlite3.connect('../Data/lonabot.db')

        c = self.connection.cursor()

        # Ensure that the Users table exist
        c.execute("CREATE TABLE IF NOT EXISTS Users"
                  "(id INTEGER PRIMARY KEY,"
                  "firstname VARCHAR, lastname VARCHAR, username VARCHAR)")

        # Ensure that the Files table exist
        c.execute("CREATE TABLE IF NOT EXISTS FileAudios"
                  "(id VARCHAR PRIMARY KEY,"
                  "telegramid VARCHAR, title VARCHAR, artist VARCHAR)")

        self.connection.commit()

    # region Users

    def close(self):
        """
        Closes the connection with the database
        :return:
        """
        self.connection.close()


    def check_user(self, user):
        """
        Checks an user in the database. If it's a new user, it's logged on console and adds it
        :param user: The user to check
        """
        c = self.connection.cursor()
        c.execute('SELECT * FROM Users WHERE id=?', (user.id,))
        if c.fetchone() is None:
            print('A new user chatted with the bot: {}'.format(user))
            c.execute("INSERT INTO Users VALUES (?, ?, ?, ?)",
                      (user.id, user.name, user.last_name, user.username,))

            self.connection.commit()

    def get_user(self, username):
        """
        Retrieves a known user
        :param username: The username of the user
        :return: The user if found, None otherwise
        """
        c = self.connection.cursor()
        c.execute('SELECT * FROM Users WHERE username=?', (username,))
        user = c.fetchone()
        if user is not None:
            return User(user)

        return None

    def user_count(self):
        """ Returns the currently logged user count """
        c = self.connection.cursor()
        c.execute('SELECT COUNT(*) FROM Users')
        return c.fetchone()[0]

    # endregion

    # region Files

    def check_file_audio(self, file_id):
        """
        Checks whether an audio file has already be sent to Telegram servers or not
        :param file_id: The ID representing the file. This may be its hash, or other ID
        :return: Telegram's ID of the file if it was sent before; None otherwise
        """
        c = self.connection.cursor()
        c.execute('SELECT telegramid FROM FileAudios WHERE id=?', (file_id,))
        result = c.fetchone()
        if result is not None:
            return result[0]

    def add_file_audio(self, file_id, telegram_id, title, artist):
        c = self.connection.cursor()
        c.execute('INSERT INTO FileAudios VALUES (?, ?, ?, ?)',
                  (file_id, telegram_id, title, artist))

        self.connection.commit()

    # endregion


"""
#!/usr/bin/python3

import sqlite3
import os.path

#conn = sqlite3.connect(':memory:')
conn = sqlite3.connect('example.db')
c = conn.cursor()

if os.path.isfile('example.db'):
    print('exists')

    t = ('RHAT',)  # Never format into string, use ? which will be replaced!
    c.execute('SELECT * FROM stocks WHERE symbol=?', t)
    print(c.fetchone())

    for row in c.execute('SELECT * FROM stocks ORDER BY price'):
        print(row)

    if input('wanna add purchases (y/n)?: ') == 'y':
        print('ok adding')
        purchases = [('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
                     ('2006-04-05', 'BUY', 'MSFT', 1000, 72.00),
                     ('2006-04-06', 'SELL', 'IBM', 500, 53.00),
                    ]
        c.executemany('INSERT INTO stocks VALUES (?,?,?,?,?)', purchases)
        conn.commit()
        conn.close()

else:
    print('pos no')

    c.execute('''CREATE TABLE stocks
                 (date text, trans text, symbol text, qty real, price real)''')

    c.execute("INSERT INTO stocks VALUES ('2006-01-05', 'BUY', 'RHAT', 100, 35.14)")

    conn.commit()
    conn.close()

"""