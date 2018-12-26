import asyncio
import functools
import random
import re
from datetime import datetime

from dumbot import Bot
from . import utils
from .constants import MAX_REMINDERS, MAX_TZ_STEP


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

HALF_AT = 0
HALF_IN = 1

MAX_DELAY_TIME = 365 * 24 * 60 * 60
CAN_U_DONT = 'CAADAgAD9RsAAuVGLgIs0peZGJA21AI'


class Lonabot(Bot):
    def __init__(self, token, db):
        super().__init__(token, timeout=10 * 60)
        self._cmd = []
        self._half_cmd = {}
        self.me = None
        self.db = db

    async def init(self):
        self.me = await self.getMe()
        self._cmd.clear()
        for m in dir(self):
            m = getattr(self, m)
            trigger = getattr(m, '_trigger', None)
            if isinstance(trigger, str):
                self._cmd.append((
                    re.compile(f'{trigger}(@{self.me.username}|[^@]|$)',
                               flags=re.IGNORECASE).match, m))

        for reminder in self.db.iter_reminders():
            self._sched_reminder(reminder.due, reminder.id)

    async def on_update(self, update):
        half, reply_id = self._half_cmd.pop(
            update.message.from_.id, (None, None))

        if not update.message.text:
            return

        for trigger, method in self._cmd:
            if trigger(update.message.text):
                await method(update)
                return

        if not update.message.reply_to_message.message_id:
            update.message.reply_to_message.message_id = reply_id

        if half is HALF_AT:
            update.message.text = f'/remindat {update.message.text}'
            await self._remindat(update)
        elif half is HALF_IN:
            update.message.text = f'/remindin {update.message.text}'
            await self._remindin(update)
        elif update.message.chat.type == 'private':
            await self.sendMessage(chat_id=update.message.from_.id,
                                   text=random.choice(SAY_WHAT))

    @cmd(r'/start')
    async def _start(self, update):
        await self.sendMessage(
            chat_id=update.message.chat.id,
            text=f'''
Hi! I'm {self.me.first_name.title()} and running in "reminder" mode.

You can set reminders by using:
`/remindin 1h30m Optional text`
`/remindat 17:05 Optional text`
`/remindat 17/11/2020 20:00 Optional text`

Or list those you have by using:
`/status`

Everyone is allowed to use {MAX_REMINDERS} reminders max. No more!

Made with love by @Lonami and hosted by Richard ❤️
'''.strip(), parse_mode='markdown')

    @limited
    @cmd(r'/remindin')
    async def _remindin(self, update):
        when = update.message.text.split(maxsplit=1)
        reply_id = update.message.reply_to_message.message_id or None

        if len(when) == 1:
            self._half_cmd[update.message.chat.id] = (HALF_IN, reply_id)
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='In when? :p')
            return

        delay, text = utils.parse_delay(when[1])
        if not delay:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='What time is that?')
        elif delay > MAX_DELAY_TIME:
            await self.sendSticker(chat_id=update.message.chat.id,
                                   sticker=CAN_U_DONT)
        else:
            due = int(datetime.utcnow().timestamp() + delay)
            reminder_id = self.db.add_reminder(update, due, text, reply_id)
            self._sched_reminder(due, reminder_id)
            spelt = utils.spell_delay(delay, prefix=False)
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text=f'Got it! Will remind in {spelt}')

    @limited
    @cmd(r'/remindat')
    async def _remindat(self, update):
        delta = self.db.get_time_delta(update.message.from_.id)
        reply_id = update.message.reply_to_message.message_id or None

        if delta is None:
            await self.sendMessage(
                chat_id=update.message.chat.id,
                text="Wait! I don't know your local time. "
                     "Please use /tz to set it first before trying again"
            )
            return

        due = update.message.text.split(maxsplit=1)
        if len(due) == 1:
            self._half_cmd[update.message.chat.id] = (HALF_AT, reply_id)
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='At what time? :p')
            return

        try:
            due, text = utils.parse_due(due[1], delta)
        except ValueError:
            await self.sendMessage(
                chat_id=update.message.chat.id,
                text='You passed a wrong date. It must '
                     'look like this:\n`DD/MM/YYYY hh:mm:ss`',
                parse_mode='markdown'
            )
            return

        if not due:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='What time is that? (The right '
                                        'format is `DD/MM/YYYY hh:mm:ss`)',
                                   parse_mode='markdown')
        elif due > int(datetime.utcnow().timestamp() + MAX_DELAY_TIME):
            await self.sendSticker(chat_id=update.message.chat.id,
                                   sticker=CAN_U_DONT)
        else:
            reminder_id = self.db.add_reminder(update, due, text, reply_id)
            self._sched_reminder(due, reminder_id)
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='Got it! Will remind you later')

    @cmd(r'/tz')
    async def _tz(self, update):
        tz = update.message.text.split(maxsplit=1)
        if len(tz) == 1:
            await self.sendMessage(
                chat_id=update.message.chat.id,
                text='Please specify your current time '
                     'in the same message as the command, '
                     'such as /tz hh:mm'
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
        reminders = list(self.db.iter_reminders(update.message.chat.id))
        delta = self.db.get_time_delta(update.message.from_.id)
        if len(reminders) == 0:
            text = "You don't have any reminder set yet. Less work for me!"
        elif len(reminders) == 1:
            reminder = reminders[0]
            due = utils.spell_due(reminder.due, delta)
            if reminder.text:
                text = f'You have one reminder {due} for "{reminder.text}"'
            else:
                text = f'You have one reminder {due}'
        else:
            if len(reminders) == MAX_REMINDERS:
                text = f'You are using all of your reminders:'
            else:
                text = f'You have {utils.spell_number(len(reminders))} ' \
                       f'reminders:'

            for i, reminder in enumerate(reminders, start=1):
                due = utils.spell_due(reminder.due, delta)
                add = reminder.text or 'no text'
                if len(add) > 40:
                    add = add[:39] + '…'
                text += f'\n({i}) {due}, {add}'

        await self.sendMessage(chat_id=update.message.chat.id, text=text,
                               parse_mode='html')

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
                                           text='Got it! The reminder is gone')
                else:
                    await self.sendMessage(chat_id=update.message.chat.id,
                                           text="You don't have that many…")
            except ValueError:
                await self.sendMessage(chat_id=update.message.chat.id,
                                       text='Er, that was not a valid number?')

    def _remind(self, reminder_id):
        reminder = self.db.pop_reminder(reminder_id)
        if reminder:
            asyncio.ensure_future(self._do_remind(reminder))

    async def _do_remind(self, reminder):
        kwargs = {}
        if reminder.chat_id > 0:  # User?
            text = reminder.text or 'Reminder'
        else:  # Group?
            kwargs['parse_mode'] = 'html'
            member = await self.getChatMember(
                chat_id=reminder.chat_id, user_id=reminder.creator_id)

            text = '<a href="tg://user?id={}">{}</a>'.format(
                reminder.creator_id, member.user.first_name or '?')

            if reminder.text:
                text += ': ' + reminder.text

        await self.sendMessage(
            chat_id=reminder.chat_id, text=text,
            reply_to_message_id=reminder.reply_to, **kwargs)

    def _sched_reminder(self, due, reminder_id):
        delta = asyncio.get_event_loop().time() - datetime.utcnow().timestamp()
        asyncio.get_event_loop().call_at(
            due + delta, functools.partial(self._remind, reminder_id))
