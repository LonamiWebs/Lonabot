from datetime import datetime

from constants import INLINE_REMINDER_LIFE


class InlineReminder:
    inline_reminders = {}

    def __init__(self, remindin, remindat):
        self._created = datetime.now()
        # Should be either None or tuples of (due, text)
        self.remindin = remindin
        self.remindat = remindat

    def should_keep(self, now):
        return now - self._created < INLINE_REMINDER_LIFE

    def add(k, v):
        InlineReminder.inline_reminders[k] = v

    def pop(k):
        return InlineReminder.inline_reminders.pop(k)

    def cleanup():
        # TODO Something like "last check" not to clean so often i.e. clean when a reminder fires but if two fire at the same time the "last check" will help.
        # Also actually call this method.
        now = datetime.now()
        InlineReminder.inline_reminders = \
            {k: v for k, v in inline_reminders.items() if v.should_keep(now)}