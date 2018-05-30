import sqlite3
import threading


DB_VERSION = 1


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
                self._upgrade_database(old=version)
                self._save()
        else:
            c.execute('CREATE TABLE Version (Version INTEGER)')
            c.execute('INSERT INTO Version VALUES (?)', (DB_VERSION,))

            c.execute('CREATE TABLE TimeDelta('
                      'UserID INTEGER PRIMARY KEY,'
                      'Delta INTEGER NOT NULL)')

            c.execute('CREATE TABLE Reminders('
                      'ID INTEGER PRIMARY KEY AUTOINCREMENT,'
                      'ChatID INTEGER NOT NULL,'
                      'Due TIMESTAMP NOT NULL,'
                      'Text TEXT NOT NULL)')

            self._save()
        c.close()

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
        pass

    def add_reminder(self, chat_id, due, text):
        c = self._cursor()
        c.execute(
            'INSERT INTO Reminders '
            '(ChatID, Due, Text) VALUES (?, ?, ?)',
            (chat_id, due, text)
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

    def get_reminders(self, chat_id):
        c = self._cursor()
        c.execute('SELECT Due, Text FROM Reminders WHERE ChatID = ? '
                  'ORDER BY Due ASC', (chat_id,))
        rows = c.fetchall()
        c.close()
        return rows

    def iter_reminders(self):
        c = self._cursor()
        c.execute('SELECT ID, Due FROM Reminders')
        row = c.fetchone()
        while row:
            yield row
            row = c.fetchone()

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
        c.execute('SELECT ChatID, Text FROM Reminders WHERE ID = ?',
                  (reminder_id,))
        row = c.fetchone()
        c.execute('DELETE FROM Reminders WHERE ID = ?', (reminder_id,))
        c.close()
        self._save()
        return row or [None] * 2
