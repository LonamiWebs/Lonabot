from datetime import datetime

from constants import INLINE_REMINDER_LIFE


class InlineReminder:
    inline_reminders = {}
    last_cleanup = datetime.now()

    def __init__(self, remindin, remindat):
        self._created = datetime.now()
        # Should be either None or tuples of (due, text)
        self.remindin = remindin
        self.remindat = remindat

    def should_keep(self, now):
        return now - self._created < INLINE_REMINDER_LIFE

    @staticmethod
    def add(k, v):
        InlineReminder.inline_reminders[k] = v

    @staticmethod
    def pop(k):
        return InlineReminder.inline_reminders.pop(k)

    @staticmethod
    def cleanup():
        now = datetime.now()
        if now - last_cleanup < INLINE_REMINDER_LIFE:
            return

        InlineReminder.inline_reminders = \
            {k: v for k, v in inline_reminders.items() if v.should_keep(now)}