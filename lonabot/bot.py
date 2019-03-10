import asyncio
import functools
import random
import re
from datetime import datetime

import dumbot
import pytz

from . import utils, heap, schedreminder, birthdays
from .constants import MAX_REMINDERS, MAX_BIRTHDAYS, MAX_TZ_STEP


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

# TODO Factor these out


def birthday_limited(f):
    @functools.wraps(f)
    async def wrapped(self, update):
        count = self.db.get_birthday_count(update.message.chat.id)
        if count < MAX_BIRTHDAYS:
            await f(self, update)
        else:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='Looks like you already have enough '
                                        'birthdays saved… Sorry about that')
    return wrapped


def private(f):
    @functools.wraps(f)
    async def wrapped(self, update):
        if update.message.chat.type == 'private':
            await f(self, update)
        else:
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text=f'Please [message me in private]'
                                        f'(tg://user?id={self._me.id}) for '
                                        f'that :)',
                                   parse_mode='markdown')
    return wrapped


SAY_WHAT = (
    'Say what?', "Sorry I didn't understand!", 'Uhm?', 'Need anything?',
    'What did you mean?', 'Are you trying to see all I can say?',
    'Not sure what to tell you!', 'Nice weather we have!',
    "True randomness doesn't always look that random…"
)

HALF_AT, HALF_IN, CONV_BD = range(3)

MAX_DELAY_TIME = 365 * 24 * 60 * 60
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


class Lonabot(dumbot.Bot):
    def __init__(self, token, db):
        super().__init__(token, timeout=10 * 60)
        self._cmd = []
        self._conversation = {}
        self._sched_reminders = None
        self._check_sched_task = None
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

        self._sched_reminders = heap.Heap(
            schedreminder.SchedReminder(r.id, r.due)
            for r in self.db.iter_reminders()
        )
        self._check_sched_task = self._loop.create_task(self._check_sched())

    async def disconnect(self):
        await super().disconnect()

        self._check_sched_task.cancel()
        try:
            await self._check_sched_task
        except asyncio.CancelledError:
            pass

    async def on_update(self, update):
        conv, data = self._conversation.pop(
            update.message.chat.id, (None, None))

        if not update.message.text:
            return

        for trigger, method in self._cmd:
            if trigger(update.message.text):
                await method(update)
                return

        if conv in (HALF_AT, HALF_IN) \
                and not update.message.reply_to_message.message_id:
            update.message.reply_to_message.message_id = data

        if conv is HALF_AT:
            update.message.text = f'/remindat {update.message.text}'
            await self._remindat(update)
        elif conv is HALF_IN:
            update.message.text = f'/remindin {update.message.text}'
            await self._remindin(update)
        elif conv is CONV_BD:
            await self._add_bday(update, data)
        elif update.message.chat.type == 'private':
            await self.sendMessage(chat_id=update.message.from_.id,
                                   text=random.choice(SAY_WHAT))

    @dumbot.command
    async def help(self, update):
        await self.start(update)

    @dumbot.command
    async def start(self, update):
        await self.sendMessage(
            chat_id=update.message.chat.id,
            text=f'''
Hi! I'm {self.me.first_name.title()} and running in "reminder" mode.

You can set reminders by using:
`/remindin 1h30m Optional text`
`/remindat 17:05 Optional text`
`/remindat 17/11/2020 20:00 Optional text`
`/remindat 2020-02-02T20:00:00+02:00 Optional text`

Or list those you have by using:
`/status`

And change your timezone for use in `/remindat` with:
`/tz 10:00`
`/tz Europe/Madrid`

Either by specifying your current time or [your location]({TZ_URL}).

Everyone is allowed to use {MAX_REMINDERS} reminders max. No more!

Made with love by @Lonami and hosted by Richard ❤️
'''.strip(), parse_mode='markdown')

    @limited
    @dumbot.command
    async def remindin(self, update):
        when = update.message.text.split(maxsplit=1)
        reply_id = update.message.reply_to_message.message_id or None

        if len(when) == 1:
            self._conversation[update.message.chat.id] = (HALF_IN, reply_id)
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
            self._sched_reminder(reminder_id, due)
            spelt = utils.spell_delay(delay, prefix=False)
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text=f'Got it! Will remind in {spelt}')

    @limited
    @dumbot.command
    async def remindat(self, update):
        delta = self.db.get_time_delta(update.message.from_.id)
        reply_id = update.message.reply_to_message.message_id or None

        due = update.message.text.split(maxsplit=1)
        if len(due) == 1:
            self._conversation[update.message.chat.id] = (HALF_AT, reply_id)
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='At what time? :p')
            return

        try:
            due, text = utils.parse_due(due[1], delta)
        except TypeError:
            await self.sendMessage(
                chat_id=update.message.chat.id,
                text="Wait! I don't know your local time. "
                     "Please use /tz to set it first before trying again"
            )
            return
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
            self._sched_reminder(reminder_id, due)
            await self.sendMessage(chat_id=update.message.chat.id,
                                   text='Got it! Will remind you later')

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
                delta = int(pytz.timezone(tz[1]).utcoffset(
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
        if which == 'bday':
            return await self._clear_bday(update)

        have = self.db.get_reminder_count(chat_id)
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
            stat = self.db.clear_nth_reminder(chat_id, from_id, 0)
            if stat == -1:
                text = 'The next reminder is not yours!'
            elif stat == 0:
                text = 'You had no reminders here'
            elif stat == 1:
                text = f'{random.choice(GOOD_BYE)} next reminder!'
        else:
            try:
                which = int(which) - 1
                if which < 0:
                    raise ValueError('Out of bounds')

                stat = self.db.clear_nth_reminder(chat_id, from_id, which)
                if stat == -1:
                    text = 'That reminder does not belong to you!'
                elif stat == 0:
                    text = "You don't have that many reminders here…"
                elif stat == 1:
                    text = 'Got it! The reminder is gone'
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

    async def _add_bday(self, update, data):
        month, day = data
        who = update.message.forward_from
        if not who:
            text = "They don't have Telegram, huh? You should tell "\
                   "them to join! Anyway, I've added the reminder!"
        elif who.id == self._me.id:
            text = "That's sweet, but that's not my birthday ❤"
        elif who.id == update.message.from_.id:
            text = "You need a reminder for your own birthday? "\
                   "Okay, I won't judge :) -- Reminder added!"
        else:
            text = 'Consider it done! I have added the reminder'

        self.db.add_birthday(
            creator_id=update.message.chat.id,
            month=month,
            day=day,
            person_id=who.id or None,
            person_name=who.first_name or update.message.text
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
                self.db.iter_birthdays(update.message.chat.id))

        )

    async def _remind(self, reminder):
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
