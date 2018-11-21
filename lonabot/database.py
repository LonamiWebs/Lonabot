import html
import sqlite3
import threading


DB_VERSION = 2


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
                      'ReplyTo INTEGER)')

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

        c.close()

    def add_reminder(self, update, due, text, reply_id):
        c = self._cursor()
        text = html.escape(text)
        if update.message.chat.type != 'private':
            text = '<a href="tg://user?id={}">{}</a>: {}'.format(
                update.message.from_.id or 0,
                update.message.from_.first_name or '?',
                text
            )

        c.execute(
            'INSERT INTO Reminders '
            '(ChatID, Due, Text, ReplyTo) VALUES (?, ?, ?, ?)',
            (update.message.chat.id, due, text, reply_id)
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

    def clear_reminders(self, chat_id):
        c = self._cursor()
        c.execute('DELETE FROM Reminders WHERE ChatID = ?', (chat_id,))
        c.close()
        self._save()

    def clear_nth_reminder(self, chat_id, n):
        c = self._cursor()
        c.execute('SELECT ID FROM Reminders WHERE ChatID = ? '
                  'ORDER BY Due ASC', (chat_id,))
        row = c.fetchone()
        while row and n:
            n -= 1
            row = c.fetchone()
        if row:
            c.execute('DELETE FROM Reminders WHERE ID = ?', row)
        c.close()
        self._save()
        return bool(row)

    def iter_reminders(self, chat_id=None):
        c = self._cursor()
        if not chat_id:
            c.execute('SELECT ID, Due FROM Reminders ORDER BY Due ASC')
        else:
            c.execute('SELECT ID, Due FROM Reminders ORDER BY Due ASC ',
                      'WHERE ChatID = ?', (chat_id,))

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
        c.execute('SELECT ChatID, Text, ReplyTo '
                  'FROM Reminders WHERE ID = ?', (reminder_id,))
        row = c.fetchone()
        c.execute('DELETE FROM Reminders WHERE ID = ?', (reminder_id,))
        c.close()
        self._save()
        return row or (None, None, None)
