import asyncio
import functools
import random
import re
from datetime import datetime

from . import utils
from .constants import MAX_REMINDERS

from dumbot.dumbaio import Bot


def cmd(text):
    def decorator(f):
        f._trigger = text
        return f
    return decorator


SAY_WHAT = (
    'Say what?', "Sorry I didn't understand!", 'Uhm?', 'Need anything?',
    'What did you mean?', 'Are you trying to see all I can say?',
    'Not sure what to tell you!', 'Nice weather we have!',
    "True randomness doesn't always look that random…"
)


class Lonabot(Bot):
    # Making Dumbot friendlier
    def __init__(self, token, db):
        super().__init__(token, timeout=10 * 60)
        self._running = False
        self._updates_loop = None
        self._last_id = 0
        self._cmd = []
        self.me = None
        self.db = db

    async def start(self):
        self._running = True
        self.me = await self.getMe()
        self._cmd.clear()
        for m in dir(self):
            m = getattr(self, m)
            trigger = getattr(m, '_trigger', None)
            if isinstance(trigger, str):
                self._cmd.append((
                    re.compile(f'{trigger}(@{self.me.username})?').match, m))

        for reminder_id, due in self.db.iter_reminders():
            self._sched_reminder(due, reminder_id)

        self._updates_loop = asyncio.ensure_future(
            self._updates_loop_impl())

    def stop(self):
        self._running = False
        if self._updates_loop:
            self._updates_loop.cancel()
            self._updates_loop = None

    async def _updates_loop_impl(self):
        while self._running:
            updates = await self.getUpdates(
                offset=self._last_id + 1, timeout=self.timeout)
            if not updates.ok or not updates.data:
                continue

            self._last_id = updates.data[-1].update_id
            for update in updates.data:
                asyncio.ensure_future(self._on_update(update))

    # Actual methods we'll be using
    async def _on_update(self, update):
        if not update.message.text:
            return

        for trigger, method in self._cmd:
            if trigger(update.message.text):
                await method(update)
                return

        await self.sendMessage(chat_id=update.message.from_.id,
                               text=random.choice(SAY_WHAT))

    @cmd(r'/start')
    async def _start(self, update):
        await self.sendMessage(
            chat_id=update.message.chat.id,
            text=f'''
Hi! I'm {self.me.first_name.title()} and running in "reminder" mode.

You can set reminders by using:
`/remindat 17:05 Optional text`
`/remindin 1h 5m Optional text`

Or list those you have by using:
`/status`

Everyone is allowed to use {MAX_REMINDERS} reminders max. No more!

Made with love by @Lonami and hosted by Richard ❤️
'''.strip(), parse_mode='markdown')

    @cmd(r'/remindin')
    async def _remindin(self, update):
        when = update.message.text.split(maxsplit=1)
        if len(when) == 1:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='In when? :p')
            return

        due, text = utils.parse_delay(when[1])
        if due:
            reminder = self.db.add_reminder(update.message.chat.id, due, text)
            self._sched_reminder(due, reminder)
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='Got it! Will remind you later')
        else:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='What time is that?')

    @cmd(r'/(remindat|status|clear)')
    async def _soon(self, update):
        await self.sendMessage(
            chat_id=update.message.chat.id,
            text='Coming soon!'
        )

    def _remind(self, reminder_id):
        chat_id, text = self.db.pop_reminder(reminder_id)
        if chat_id:
            asyncio.ensure_future(self.sendMessage(chat_id=chat_id, text=text))

    def _sched_reminder(self, due, reminder_id):
        delta = asyncio.get_event_loop().time() - datetime.utcnow().timestamp()
        asyncio.get_event_loop().call_at(
            due + delta, functools.partial(self._remind, reminder_id))
