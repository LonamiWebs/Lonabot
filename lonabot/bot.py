import asyncio
import calendar
import contextlib
import functools
import html
import logging
import random
import re
from datetime import datetime, timedelta

import dumbot
import pytz

from . import utils, heap, schedreminder, birthdays, database
from .constants import MAX_REMINDERS, MAX_BIRTHDAYS, MAX_TZ_STEP


def limited(f):
    @functools.wraps(f)
    async def wrapped(self, update, *args):
        count = self.db.get_reminder_count(update.message.from_.id)
        if count < MAX_REMINDERS:
            await f(self, update, *args)
        else:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='Looks like you already have enough '
                                        'reminders… Sorry about that')
    return wrapped

# TODO Factor these out


def birthday_limited(f):
    @functools.wraps(f)
    async def wrapped(self, update, *args):
        count = self.db.get_birthday_count(update.message.from_.id)
        if count < MAX_BIRTHDAYS:
            await f(self, update, *args)
        else:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='Looks like you already have enough '
                                        'birthdays saved… Sorry about that')
    return wrapped


def private(f):
    @functools.wraps(f)
    async def wrapped(self, update, *args):
        if update.message.chat.type == 'private':
            await f(self, update, *args)
        else:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text=f'Please [message me in private]'
                                        f'(tg://user?id={self._me.id}) for '
                                        f'that ;)',
                                   parse_mode='markdown')
    return wrapped


def log_exc(f):
    @functools.wraps(f)
    async def wrapped(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except Exception:
            logging.exception('Unhandled exception in %s', f)

    return wrapped


TEACH_USAGE = '''
You can set reminders by using:
`/remind 1h30m Optional text`
`/remind 17:05 Optional text`
`/remind 17/11/2020 20:00 Optional text`
`/remind 2020-02-02T20:00:00+02:00 Optional text`
'''.strip()

SAY_WHAT = (
    'Say what?', "Sorry I didn't understand!", 'Uhm?', 'Need anything?',
    'What did you mean?', 'Are you trying to see all I can say?',
    'Not sure what to tell you!', 'Nice weather we have!',
    "True randomness doesn't always look that random…"
)

CONV_BD = 0

LONG_DELAY_TIME = 1 * 365 * 24 * 60 * 60
MAX_DELAY_TIME = 5 * 365 * 24 * 60 * 60
MAX_TZ_DELTA = 12 * 60 * 60
CAN_U_DONT = 'CAADAgAD9RsAAuVGLgIs0peZGJA21AI'

TZ_URL = 'https://raw.githubusercontent.com/newvem/pytz/master/pytz/zone.tab'

GOOD_BYE = [
    'Goodbye',
    'Zdravo',
    'Joigin',
    'Donadagohvi',
    'Sbohem',
    'Farvel',
    'Farväl',
    'Hejdå',
    'Tot ziens',
    'Näkemiin',
    'Au revoir',
    'Yasou',
    'Aloha',
    'Namaste',
    'Slan',
    'Arrivederci',
    'Atsiprasau',
    'Adeus',
    'Alweda',
    'Adiós',
    'Hamba kahle',
    'Sayonara',
]

FACES = [
    '^^',
    ':)',
    ';)',
    ':D',
    '❤',
]


class Lonabot(dumbot.Bot):
    def __init__(self, token: str, db: database.Database):
        super().__init__(token, timeout=10 * 60)
        self._conversation = {}
        self._sched_reminders = None
        self._check_sched_task = None
        self._check_bday_task = None
        self._thanks = None
        self.db = db

    async def init(self):
        self._thanks = re.compile(
            rf'(?i)(ty|thank(s|\s*you))'
            rf'\s*(vm|very\s*much)?'
            rf'\s*@?({self._me.first_name}|{self._me.username})'
            rf'[\n .!]*$'
        ).match

        self._sched_reminders = heap.Heap(
            schedreminder.SchedReminder(r.id, r.due)
            for r in self.db.iter_reminders()
        )
        self._check_sched_task = self._loop.create_task(self._check_sched())
        self._check_bday_task = self._loop.create_task(self._check_bday())

    async def disconnect(self):
        await super().disconnect()

        self._check_sched_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._check_sched_task

        self._check_bday_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._check_bday_task

    async def on_update(self, update):
        msg = update.message
        conv, data = self._conversation.pop(msg.chat.id, (None, None))
        text = msg.text or msg.caption
        if not text:
            return

        if conv is CONV_BD:
            await self._add_bday(update, data)
        elif self._thanks(text):
            await self.sendMessage(
                chat_id=msg.chat.id,
                text=f"You're welcome {msg.from_.first_name} "
                     f"{random.choice(FACES)}"
            )
        elif msg.chat.type == 'private' and not msg.forward_date:
            await self.sendMessage(chat_id=msg.from_.id,
                                   text=random.choice(SAY_WHAT))

    @dumbot.command
    async def help(self, update):
        await self.start(update)

    @dumbot.command
    async def start(self, update):
        await self.sendMessage(
            chat_id=update.message.chat.id,
            text=f'''
Hi! I'm {self._me.first_name.title()} and running in "reminder" mode.

{TEACH_USAGE}

Or list those you have by using:
`/status`

And change your timezone for use in `/remindat` with:
`/tz 10:00`
`/tz Europe/Madrid`

Either by specifying your current time or [your location]({TZ_URL}).

Everyone is allowed to use {MAX_REMINDERS} reminders max. No more!

Made with love by @Lonami and hosted by Richard ❤️
'''.strip(), parse_mode='markdown')

    @dumbot.command
    async def remindin(self, update):
        await self.remind(update)

    @dumbot.command
    async def remindat(self, update):
        await self.remind(update)

    @limited
    @dumbot.command
    async def remind(self, update):
        msg = update.message
        chat_id = msg.chat.id

        delta = self.db.get_time_delta(msg.from_.id)
        reply_id = update.message.reply_to_message.message_id or None

        text, file_type, file_id = utils.split_message(msg)
        when = text.split(maxsplit=1)
        if len(when) == 1:
            sent = await self.sendMessage(
                chat_id=chat_id,
                text='You forgot to specify when, silly 😉'
                     '(e.g. `/remind 1h30m` or `/remind 17:30`)',
                parse_mode='markdown'
            )

            if msg.chat.type != 'private':
                await asyncio.sleep(10)
                await self.deleteMessage(chat_id=chat_id,
                                         message_id=sent.message_id)
            return

        try:
            due, text = utils.parse_when(when[1], delta)
        except ValueError:
            await self.sendMessage(
                chat_id=chat_id,
                text="Wait! I don't know your local time. "
                     "Please use /tz to set it first before trying again"
            )
            return

        if not due:
            if msg.chat.type == 'private':
                await self.sendMessage(
                    chat_id=chat_id,
                    text=f'What time is that?\n\n{TEACH_USAGE}',
                    parse_mode='markdown'
                )
            else:
                await self.sendMessage(
                    chat_id=chat_id,
                    text=f'What time is that? ([Start me in private]'
                         f'(https://t.me/{self._me.username}?start=help) for help)',
                    parse_mode='markdown',
                    disable_web_page_preview=True
                )
        elif due > int(datetime.utcnow().timestamp() + MAX_DELAY_TIME):
            await self.sendSticker(chat_id=chat_id,
                                   sticker=CAN_U_DONT)
        else:
            reminder_id = self.db.add_reminder(
                update=update,
                due=due,
                text=text,
                file_type=file_type,
                file_id=file_id,
                reply_id=reply_id
            )
            self._sched_reminder(reminder_id, due)
            spelt = utils.spell_due(due, delta)
            await self.sendMessage(chat_id=chat_id,
                                   text=f'Got it! New reminder {spelt} saved')

    @dumbot.command
    async def tz(self, update):
        tz = update.message.text.split(maxsplit=1)
        if len(tz) == 1:
            await self.sendMessage(
                chat_id=update.message.chat.id,
                text='Please specify your current time '
                     'in the same message as the command, '
                     'such as /tz hh:mm or /tz Europe/Andorra'
            )
            return

        delta = None
        m = re.match(r'(\d+):(\d+)', tz[1])
        if m:
            hour, mins = map(int, m.groups())
        else:
            try:
                # TODO This won't consider daylight saving time BS
                # TODO Do this delta thing better
                delta = int(pytz.timezone(tz[1].title()).utcoffset(
                    datetime.utcnow()).total_seconds())

            except pytz.UnknownTimeZoneError:
                await self.sendMessage(
                    chat_id=update.message.chat.id,
                    text=f'Sorry, not a clue where that is. Here is a list '
                         f'with the [timezones I know]({TZ_URL}) '
                         f'or use a time like /tz hh:mm.',
                    parse_mode='markdown'
                )
                return

        if delta is None:
            now = datetime.utcnow()
            now = now.hour * 60 + now.minute
            remote = hour * 60 + mins

            delta = utils.large_round(remote - now, MAX_TZ_STEP) * 60

            # Check that we're within the same day or the delta will be wrong
            if abs(delta) > MAX_TZ_DELTA:
                if delta < 0:
                    delta += 24 * 60 * 60
                else:
                    delta -= 24 * 60 * 60

        self.db.set_time_delta(update.message.from_.id, delta)
        await self.sendMessage(chat_id=update.message.chat.id,
                               text=f"Got it! There's a difference of "
                                    f"{delta} seconds between you and I :D")

    @dumbot.command
    async def status(self, update):
        chat_id = update.message.chat.id
        from_id = update.message.from_.id

        reminders = list(self.db.iter_reminders(chat_id, from_id))
        delta = self.db.get_time_delta(from_id)
        if len(reminders) == 0:
            text = "You don't have any reminder in this chat yet"
        elif len(reminders) == 1:
            reminder = reminders[0]
            due = utils.spell_due(reminder.due, delta)
            if reminder.text:
                text = f'You have one reminder {due} here for "{reminder.text}"'
            else:
                text = f'You have one reminder {due} here'
        else:
            text = f'You have {utils.spell_number(len(reminders))} ' \
                   f'reminders in this chat:'

            for i, reminder in enumerate(reminders, start=1):
                due = utils.spell_due(reminder.due, delta)
                add = reminder.text or 'no text'
                if len(add) > 40:
                    add = add[:39] + '…'
                text += f'\n({i}) {due}, {add}'

        if update.message.chat.type == 'private':
            count = self.db.get_birthday_count(chat_id)
            if count == 0:
                text += '\n\nYou have not saved any birthdays here yet'
            else:
                s = '' if count == 1 else 's'
                text += f'\n\nYou have {count} birthday{s} saved:'
                for r in self.db.iter_birthdays(update.message.chat.id):
                    text += f'\n• {r.person_name} ({r.day} {calendar.month_name[r.month]})'

        await self.sendMessage(chat_id=chat_id, text=text, parse_mode='html')

    @dumbot.command
    async def clear(self, update):
        chat_id = update.message.chat.id
        from_id = update.message.from_.id
        which = update.message.text.split(maxsplit=1)
        if len(which) == 1:
            await self.sendMessage(
                chat_id=chat_id,
                text='Please specify "all", "next", "bday" or '
                     'the number shown in /status (no quotes!)'
            )
            return

        which = which[1].lower()
        if which in ('bday', 'birthday'):
            return await self._clear_bday(update)

        have = self.db.get_reminder_count(from_id)
        if not have:
            shrug = b'\xf0\x9f\xa4\xb7\xe2\x80\x8d\xe2\x99\x80\xef\xb8\x8f'
            await self.sendMessage(  # ^ haha unicode
                chat_id=chat_id,
                text=f'Nothing to clear {str(shrug, encoding="utf-8")}'
            )
            return

        text = 'Beep boop, logic error - bug my owner to fix me'
        if which == 'all':
            self.db.clear_reminders(chat_id, from_id)
            if chat_id == from_id:
                text = 'Poof \U0001f4ad! All be gone!'
            else:
                text = 'Poof \U0001f4ad! All your reminders here be gone!'
        elif which == 'next':
            if self.db.clear_nth_reminder(chat_id, from_id, 0):
                text = f'{random.choice(GOOD_BYE)} next reminder!'
            else:
                text = 'You had no reminders here'
        else:
            try:
                which = int(which) - 1
                if which < 0:
                    raise ValueError('Out of bounds')

                if self.db.clear_nth_reminder(chat_id, from_id, which):
                    text = 'Got it! The reminder is gone'
                else:
                    text = "You don't have that many reminders here…"
            except ValueError:
                text = 'Er, that was not a valid number?'

        await self.sendMessage(chat_id=chat_id, text=text)

    # Birthdays

    # Note: we assume Telegram doesn't let send people arbitrary payload.
    #       Otherwise, they could bypass this main command and just send data.
    #       We also rely on this fact to clear birthdays.
    @private
    @birthday_limited
    @dumbot.command
    async def remindbday(self, update):
        await self.sendMessage(
            chat_id=update.message.chat.id,
            text="Let's add a birthday! First, "
                 "select your friend's birthday month",
            reply_markup=birthdays.MONTH_MARKUP
        )

    @dumbot.inline_button(r'cancel')
    async def cancel(self, update, match):
        message = update.callback_query.message
        await self.editMessageText(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text='Okay, operation cancelled'
        )

    @dumbot.inline_button(r'birthday/add/m(\d+)')
    async def month(self, update, match):
        message = update.callback_query.message
        await self.editMessageText(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text='Now please select the day of their birthday, '
                 'or click the name of the month to change it',
            reply_markup=birthdays.MONTH_DAY_MARKUP[int(match.group(1)) - 1]
        )

    @dumbot.inline_button(r'birthday/add/y')
    async def year(self, update, match):
        message = update.callback_query.message
        await self.editMessageText(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text='Different month? No problem :) Please select '
                 'the month of their birthday once again',
            reply_markup=birthdays.MONTH_MARKUP
        )

    @dumbot.inline_button(r'birthday/add/m(\d+)d(\d+)')
    async def day(self, update, match):
        message = update.callback_query.message
        self._conversation[message.chat.id] = CONV_BD, match.groups()
        await self.editMessageText(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text='Almost done! Forward me a message sent by that '
                 'person or send me their name so that I can remind '
                 'you about them with a nice click-able mention ^^'
        )

    @dumbot.command
    async def stats(self, update):
        people_count, reminder_count = self.db.stats()
        if reminder_count == 0:
            text = 'I am currently procrastinating :)'
        elif reminder_count == 1:
            text = "I'm only pending of one reminder at the moment"
        elif reminder_count < 10:
            text = f"I'm not doing much, just have {reminder_count} reminders"
        else:
            noun = 'person' if people_count == 1 else 'people'
            text = f"I'm pending of {reminder_count} reminders for {people_count} {noun}"

        await self.sendMessage(chat_id=update.message.chat.id, text=text)

    async def _add_bday(self, update, data):
        def get_info():
            fwd = update.message.forward_from
            if fwd:
                return fwd.id, fwd.username, fwd.first_name

            for m in update.message.entities:
                if m.type == 'mention':
                    usr = update.message.text[m.offset:m.offset + m.length]
                    return None, usr, usr
                elif m.type == 'text_mention':
                    return m.user.id, m.user.first_name, m.user.first_name

            return None, None, update.message.text

        who_id, who_username, who_name = get_info()

        month, day = data
        if not who_id and not who_username:
            text = "They don't have Telegram, huh? You should tell "\
                   "them to join! Anyway, I've added the reminder!"
        elif who_id == self._me.id:
            text = "That's sweet, but that's not my birthday ❤"
        elif who_id == update.message.from_.id:
            text = "You need a reminder for your own birthday? "\
                   "Okay, I won't judge :) -- Reminder added!"
        else:
            text = 'Consider it done! I have added the reminder'

        self.db.add_birthday(
            creator_id=update.message.chat.id,
            month=month,
            day=day,
            person_id=who_id or None,
            person_name=who_name
        )
        await self.sendMessage(
            chat_id=update.message.chat.id,
            text=text
        )

    @private
    async def _clear_bday(self, update):
        count = self.db.get_birthday_count(update.message.chat.id)
        if not count:
            await self.sendMessage(
                chat_id=update.message.chat.id,
                text='You have not saved any birthday with me yet'
            )
            return

        await self.sendMessage(
            chat_id=update.message.chat.id,
            text='Which birthday do you want to remove?',
            reply_markup=birthdays.build_clear_markup(
                self.db.iter_birthdays(update.message.chat.id))
        )

    @dumbot.inline_button(r'birthday/clear/(\d+)')
    async def _delete_bday(self, update, match):
        self.db.delete_birthday(int(match.group(1)))

        message = update.callback_query.message
        count = self.db.get_birthday_count(message.chat.id)
        if not count:
            await self.sendMessage(
                chat_id=message.chat.id,
                text='I have deleted all your saved birthdays now :)'
            )
            return

        await self.editMessageText(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text='Gone! Any other to remove?',
            reply_markup=birthdays.build_clear_markup(
                self.db.iter_birthdays(message.chat.id))
        )

    async def _remind(self, reminder):
        kwargs = {
            'chat_id': reminder.chat_id,
            'reply_to_message_id': reminder.reply_to
        }
        if reminder.chat_id > 0:  # User?
            text = reminder.text
            if not text and not reminder.file_type:
                text = 'Reminder'
        else:  # Group?
            kwargs['parse_mode'] = 'html'
            member = await self.getChatMember(
                chat_id=reminder.chat_id, user_id=reminder.creator_id)

            text = '<a href="tg://user?id={}">{}</a>'.format(
                reminder.creator_id, member.user.first_name or '?')

            if reminder.text:
                text += ': ' + reminder.text

        if reminder.file_type:
            method = getattr(self, f'send{reminder.file_type.title()}')
            kwargs[reminder.file_type] = reminder.file_id
            kwargs['caption'] = text
        else:
            method = self.sendMessage
            kwargs['text'] = text

        await method(**kwargs)

    @log_exc
    async def _check_sched(self):
        while self._running:
            while self._sched_reminders:
                upcoming = self._sched_reminders.peek()
                delta = upcoming.due - datetime.utcnow().timestamp()
                if delta > 1:
                    break

                await asyncio.sleep(delta)
                self._sched_reminders.pop()
                reminder = self.db.pop_reminder(upcoming.id)
                if reminder:
                    self._loop.create_task(self._remind(reminder))

            await asyncio.sleep(1)

    def _sched_reminder(self, reminder_id, due):
        self._sched_reminders.push(
            schedreminder.SchedReminder(reminder_id, due))

    @log_exc
    async def _check_bday(self):
        while self._running:
            day = datetime.utcnow()
            for bday in self.db.iter_birthdays(month=day.month, day=day.day):
                if not self.db.has_birthday_stage(bday.id, day.year, stage=2):
                    await self._remind_bday(bday, today=True)
                    self.db.set_birthday_stage(bday.id, day.year, stage=2)

            day += timedelta(days=1)
            for bday in self.db.iter_birthdays(month=day.month, day=day.day):
                if not self.db.has_birthday_stage(bday.id, day.year, stage=1):
                    await self._remind_bday(bday, today=False)
                    self.db.set_birthday_stage(bday.id, day.year, stage=1)

            await asyncio.sleep(6 * 60 * 60)

    async def _remind_bday(self, bday, today):
        name = html.escape(bday.person_name)
        if name.lower().endswith('s'):
            postfix = "'"
        else:
            postfix = "'s"

        if bday.person_id:
            mention = f'<a href="tg://user?id={bday.person_id}">{name}</a>'
        else:
            mention = name

        if today:
            text = f"Today it's {mention}{postfix} birthday! 🎉"
        else:
            text = f"Tomorrow it's {mention}{postfix} birthday. "\
                   f"Did you get them a present yet 🎁?"

        await self.sendMessage(
            chat_id=bday.creator_id,
            text=text,
            parse_mode='html'
        )
        await asyncio.sleep(1)
