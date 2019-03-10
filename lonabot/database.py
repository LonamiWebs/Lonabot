import collections
import sqlite3
import threading

DB_VERSION = 4


Reminder = collections.namedtuple(
    'Reminder', 'id chat_id due text reply_to creator_id')

Birthday = collections.namedtuple(
    'Birthday', 'id creator_id month day person_id person_name')


class Database:
    def __init__(self, filename):
        self._filename = filename
        self._conns = {}

        c = self._cursor()
        c.execute("SELECT name FROM sqlite_master "
                  "WHERE type='table' AND name='Version'")

        if c.fetchone():
            c.execute('SELECT Version FROM Version')
            version = c.fetchone()[0]
            if version != DB_VERSION:
                self._set_version(c, drop=True)
                self._upgrade_database(old=version)
                self._save()
        else:
            self._set_version(c, drop=False)

            c.execute('CREATE TABLE TimeDelta('
                      'UserID INTEGER PRIMARY KEY,'
                      'Delta INTEGER NOT NULL)')

            c.execute('CREATE TABLE Reminders('
                      'ID INTEGER PRIMARY KEY AUTOINCREMENT,'
                      'ChatID INTEGER NOT NULL,'
                      'Due TIMESTAMP NOT NULL,'
                      'Text TEXT NOT NULL,'
                      'ReplyTo INTEGER,'
                      'CreatorID INTEGER NOT NULL)')

            c.execute('CREATE TABLE Birthdays('
                      'ID INTEGER PRIMARY KEY AUTOINCREMENT,'
                      'CreatorID INTEGER NOT NULL,'
                      'Month INTEGER NOT NULL,'
                      'Day INTEGER NOT NULL,'
                      'PersonID INTEGER,'
                      'PersonName TEXT)')

            self._save()
        c.close()

    @staticmethod
    def _set_version(c, *, drop):
        if drop:
            c.execute('DROP TABLE Version')

        c.execute('CREATE TABLE Version (Version INTEGER)')
        c.execute('INSERT INTO Version VALUES (?)', (DB_VERSION,))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        for conn in self._conns.values():
            try:
                conn.close()
            except:
                pass
        self._conns.clear()

    def _save(self):
        conn = self._conns.get(threading.get_ident())
        if conn:
            conn.commit()

    def _cursor(self):
        conn = self._conns.get(threading.get_ident())
        if conn is None:
            self._conns[threading.get_ident()] = conn =\
                sqlite3.connect(self._filename)
        return conn.cursor()

    def _upgrade_database(self, old):
        c = self._cursor()
        if old == 1:
            c.execute('ALTER TABLE Reminders ADD ReplyTo INTEGER')
            old = 2
        if old == 2:
            c.execute('ALTER TABLE Reminders ADD CreatorID INTEGER '
                      'NOT NULL DEFAULT 0')
            old = 3
        if old == 3:
            c.execute('CREATE TABLE Birthdays('
                      'ID INTEGER PRIMARY KEY AUTOINCREMENT,'
                      'CreatorID INTEGER NOT NULL,'
                      'Month INTEGER NOT NULL,'
                      'Day INTEGER NOT NULL,'
                      'PersonID INTEGER,'
                      'PersonName TEXT)')

        c.close()

    def add_reminder(self, update, due, text, reply_id):
        c = self._cursor()
        m = update.message
        c.execute(
            'INSERT INTO Reminders '
            '(ChatID, CreatorID, Due, Text, ReplyTo) VALUES (?, ?, ?, ?, ?)',
            (m.chat.id, m.from_.id, due, text.strip(), reply_id)
        )
        new_id = c.lastrowid
        c.close()
        self._save()
        return new_id

    def get_reminder_count(self, chat_id):
        c = self._cursor()
        c.execute('SELECT COUNT(*) FROM Reminders WHERE ChatID = ?',
                  (chat_id,))
        count = c.fetchone()[0]
        c.close()
        return count

    def clear_reminders(self, chat_id, from_id):
        c = self._cursor()
        c.execute('DELETE FROM Reminders WHERE '
                  'ChatID = ? AND CreatorID = ?', (chat_id, from_id))
        c.close()
        self._save()

    def clear_nth_reminder(self, chat_id, from_id, n):
        c = self._cursor()
        c.execute('SELECT * FROM Reminders WHERE ChatID = ? '
                  'ORDER BY Due ASC', (chat_id,))
        row = c.fetchone()
        while row and n:
            n -= 1
            row = c.fetchone()

        if row:
            row = Reminder(*row)
            if row.creator_id == from_id:
                stat = +1
                c.execute('DELETE FROM Reminders WHERE ID = ?', (row.id,))
            else:
                stat = -1
        else:
            stat = 0

        c.close()
        self._save()
        return stat

    def iter_reminders(self, chat_id=None):
        c = self._cursor()
        if chat_id:
            c.execute('SELECT * FROM Reminders WHERE ChatID = ? '
                      'ORDER BY Due ASC', (chat_id,))
        else:
            c.execute('SELECT * FROM Reminders ORDER BY Due ASC')

        row = c.fetchone()
        while row:
            yield Reminder(*row)
            row = c.fetchone()

        c.close()

    def set_time_delta(self, user_id, delta):
        c = self._cursor()
        c.execute(
            'INSERT OR REPLACE INTO TimeDelta '
            '(UserID, Delta) VALUES (?, ?)',
            (user_id, delta)
        )
        c.close()
        self._save()

    def get_time_delta(self, user_id):
        c = self._cursor()
        c.execute('SELECT Delta FROM TimeDelta WHERE UserID = ?', (user_id,))
        return (c.fetchone() or (None,))[0]

    def pop_reminder(self, reminder_id):
        c = self._cursor()
        c.execute('SELECT * FROM Reminders WHERE ID = ?', (reminder_id,))
        row = c.fetchone()
        c.execute('DELETE FROM Reminders WHERE ID = ?', (reminder_id,))
        c.close()
        self._save()
        return Reminder(*row) if row else None

    def add_birthday(self, creator_id, month, day, person_id, person_name):
        c = self._cursor()
        c.execute(
            'INSERT INTO Birthdays '
            '(CreatorID, Month, Day, PersonID, PersonName) VALUES (?, ?, ?, ?, ?)',
            (creator_id, month, day, person_id, person_name)
        )
        c.close()
        self._save()

    # TODO Factor these out (similar to get_reminder_count and iter_reminders)
    def get_birthday_count(self, creator_id):
        c = self._cursor()
        c.execute('SELECT COUNT(*) FROM Birthdays WHERE CreatorID = ?',
                  (creator_id,))
        count = c.fetchone()[0]
        c.close()
        return count

    def iter_birthdays(self, creator_id=None):
        c = self._cursor()
        if creator_id:
            c.execute('SELECT * FROM Birthdays WHERE CreatorID = ? '
                      'ORDER BY Month ASC, Day ASC', (creator_id,))
        else:
            c.execute('SELECT * FROM Birthdays ORDER BY Month ASC, Day ASC')

        row = c.fetchone()
        while row:
            yield Birthday(*row)
            row = c.fetchone()

        c.close()

    def delete_birthday(self, birthday_id):
        c = self._cursor()
        c.execute('DELETE FROM Birthdays WHERE ID = ?', (birthday_id,))
        c.close()
