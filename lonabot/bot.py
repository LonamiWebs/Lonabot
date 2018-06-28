import asyncio
import functools
import random
import re
from datetime import datetime

from . import utils
from .constants import MAX_REMINDERS, MAX_TZ_STEP

from dumbot.dumbaio import Bot


def cmd(text):
    def decorator(f):
        f._trigger = text
        return f
    return decorator


def limited(f):
    @functools.wraps(f)
    async def wrapped(self, update):
        count = self.db.get_reminder_count(update.message.chat.id)
        if count < MAX_REMINDERS:
            await f(self, update)
        else:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='Looks like you already have enough '
                                        'reminders… Sorry about that')
    return wrapped


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
                    re.compile(f'{trigger}(@{self.me.username})?',
                               flags=re.IGNORECASE).match, m))

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

        if update.message.chat.type == 'private':
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

    @limited
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
            delay = utils.spell_due(due, prefix=False)
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text=f'Got it! Will remind in {delay}')
        else:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='What time is that?')

    @limited
    @cmd(r'/remindat')
    async def _remindat(self, update):
        delta = self.db.get_time_delta(update.message.from_.id)
        if delta is None:
            await self.sendMessage(
                chat_id=update.message.chat.id,
                text="Wait! I don't know your local time. "
                     "Please use /tz to set it first before trying again"
            )
            return

        due = update.message.text.split(maxsplit=1)
        if len(due) == 1:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='At what time? :p')
            return

        due, text = utils.parse_due(due[1], delta)
        if due:
            reminder = self.db.add_reminder(update.message.chat.id, due, text)
            self._sched_reminder(due, reminder)
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='Got it! Will remind you later')
        else:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='What time is that?')

    @cmd(r'/tz')
    async def _tz(self, update):
        tz = update.message.text.split(maxsplit=1)
        if len(tz) == 1:
            await self.sendMessage(
                chat_id=update.message.chat.id,
                text='Please specify your current time '
                     'in the same message as the command!'
            )
            return

        m = re.match(r'(\d+):(\d+)', tz[1])
        if not m:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='The time must be like /tz hh:mm')
            return

        now = datetime.utcnow()
        now = utils.large_round(now.hour * 60 + now.minute, MAX_TZ_STEP)
        remote = int(m.group(1)) * 60 + int(m.group(2))
        remote = utils.large_round(remote, MAX_TZ_STEP)

        delta = (remote - now) * 60
        self.db.set_time_delta(update.message.from_.id, delta)
        await self.sendMessage(chat_id=update.message.chat.id,
                               text=f"Got it! There's a difference of "
                                    f"{delta} seconds between you and I :D")

    @cmd(r'/status')
    async def _status(self, update):
        reminders = self.db.get_reminders(update.message.chat.id)
        delta = self.db.get_time_delta(update.message.from_.id)
        if len(reminders) == 0:
            text = "You don't have any reminder set yet. Less work for me!"
        elif len(reminders) == 1:
            due, reminder = reminders[0]
            due = utils.spell_due(due, delta)
            if reminder:
                text = f'You have one reminder {due} for "{reminder}"'
            else:
                text = f'You have one reminder {due}'
        else:
            if len(reminders) == MAX_REMINDERS:
                text = f'You are using all of your reminders:'
            else:
                text = f'You have {utils.spell_number(len(reminders))} ' \
                       f'reminders:'

            for i, t in enumerate(reminders, start=1):
                due, reminder = t
                due = utils.spell_due(due, delta)
                if not reminder:
                    reminder = 'no text'
                elif len(reminder) > 40:
                    reminder = reminder[:39] + '…'
                text += f'\n({i}) {due}, {reminder}'

        await self.sendMessage(chat_id=update.message.chat.id, text=text)

    @cmd(r'/clear')
    async def _clear(self, update):
        have = self.db.get_reminder_count(update.message.chat.id)
        if not have:
            shrug = b'\xf0\x9f\xa4\xb7\xe2\x80\x8d\xe2\x99\x80\xef\xb8\x8f'
            await self.sendMessage(  # ^ haha unicode
                chat_id=update.message.chat.id,
                text=f'Nothing to clear {str(shrug, encoding="utf-8")}'
            )
            return

        which = update.message.text.split(maxsplit=1)
        if len(which) == 1:
            await self.sendMessage(
                chat_id=update.message.chat.id,
                text='Please specify "all", "next" or '
                     'the number shown in /status (no quotes!)'
            )
            return

        which = which[1].lower()
        if which == 'all':
            self.db.clear_reminders(update.message.chat.id)
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text=f'Poof {chr(128173)}! All be gone!')
        elif which == 'next':
            self.db.clear_nth_reminder(update.message.chat.id, 0)
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text=f'Sayonara next reminder!')
        else:
            try:
                which = int(which) - 1
                if which < 0:
                    raise ValueError('Out of bounds')

                if self.db.clear_nth_reminder(update.message.chat.id, which):
                    await self.sendMessage(chat_id=update.message.chat.id,
                                           text='Got it! The reminder gone')
                else:
                    await self.sendMessage(chat_id=update.message.chat.id,
                                           text="You don't have that many…")
            except ValueError:
                await self.sendMessage(chat_id=update.message.chat.id,
                                       text='Er, that was not a valid number?')

    def _remind(self, reminder_id):
        chat_id, text = self.db.pop_reminder(reminder_id)
        if chat_id:
            asyncio.ensure_future(self.sendMessage(chat_id=chat_id, text=text))

    def _sched_reminder(self, due, reminder_id):
        delta = asyncio.get_event_loop().time() - datetime.utcnow().timestamp()
        asyncio.get_event_loop().call_at(
            due + delta, functools.partial(self._remind, reminder_id))
