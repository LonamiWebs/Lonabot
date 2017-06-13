#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
#
# Reminder bot
from telegram import (
    ParseMode, InlineQueryResultArticle, InputTextMessageContent,
    ReplyKeyboardMarkup, ReplyKeyboardRemove
)

from telegram.ext import (
    Updater, CommandHandler, InlineQueryHandler, MessageHandler, Filters,
    ConversationHandler, RegexHandler
)

from datetime import datetime, timedelta, time
from uuid import uuid4
import logging
import os
import re


# Constants
MAX_REMINDERS = 10
MAX_DATA_PER_REMINDER_BYTES = 256
INLINE_REMINDER_LIFE = timedelta(seconds=30)


class InlineReminder:
    def __init__(self, remindin, remindat):
        self._created = datetime.now()
        # Should be either None or tuples of (due, text)
        self.remindin = remindin
        self.remindat = remindat

    def should_keep(self, now):
        return now - self._created < INLINE_REMINDER_LIFE


REMINDIN_RE = re.compile(r'''
^
(?:  # First option

    (                # # MATCH 1: 'hh:mm:ss' or 'mm:ss'
        \d+          # Minutes or hours
        \s*:\s*      # ':'
        \d+          # Seconds or minutes
        (?:
            \s*:\s*  # ':'
            \d+      # Seconds, then the others are hours:minutes
        )?
    )

)
|
(?:  # Second option

    (                # # # MATCH 2: 'uu' for "units"
        \d+          # Which are a few digits
        (?:
            [,.]\d+  # Possibly capture a value after the decimal point
        )?
    )
    \s*              # Some people like to separate units from the number

    (                # # # MATCH 3: '(d|h|m|s).*' for days, hours, mins, secs
        d(?:ays?)?         # Either 'd', 'day' or 'days'
        |                  # or
        h(?:ours?)?        # Either 'h', 'hour' or 'hours'
        |                  # or
        m(?:in(?:ute)?s?)? # Either 'm', 'min', 'mins', 'minute' or 'minutes'
        |                  # or
        s(?:ec(?:ond)?s?)? # Either 's', 'sec', 'secs', 'second' or 'seconds'
    )?

)\b''', re.IGNORECASE | re.VERBOSE)


REMINDAT_RE = re.compile(r'''
^
(?:  # First option

    (                 # # MATCH 1: 'hh' or 'hh:mm' or 'hh:mm:ss'
        \d+           # Hours
        (?:
            :\d+      # Possibly minutes
            (?:
                :\d+  # Possibly seconds
            )?
        )?
    )
    \s*               # Some people like to separate am/pm from the time

    (?:               # Don't capture the whole am/pm stuff
        (?:           # Don't capture the p|a options

            (p)       # # MATCH 2: Only capture 'p', because that's when +12h
            |         # Either 'p' or
            a         # 'a'

        )
        m        # It is either 'am' or 'pm'
    )?

)\b''', re.IGNORECASE | re.VERBOSE)


# Temporary variables
inline_reminders = {}
def cleanup_inline_reminders():
    # TODO Something like "last check" not to clean so often i.e. clean when a reminder fires but if two fire at the same time the "last check" will help.
    # Also actually call this method.
    global inline_reminders
    now = datetime.now()
    inline_reminders = {k: v for k, v in inline_reminders.items()
                             if v.should_keep(now)}


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Utilities
def from_admin(update):
    """Is this update from the admin?"""
    return update.message.from_user.id == 10885151


def parsehour(text, reverse):
    """Small utility to parse hours (18:05), or optionally reversing
       it to first detect the seconds, then minutes, then hours.
    """
    parts = text.split(':')
    if len(parts) > 3:
        parts = parts[-3:]

    due = 0
    try:
        if reverse:
            for u, p in zip((1, 60, 3600), reversed(parts)):
                due += u * int(p)
        else:
            for u, p in zip((3600, 60, 1), parts):
                due += u * int(p)

        return due
    except ValueError:
        pass     


def format_time_diff(to_date):
    """Formats the time difference between now and to_date"""
    diff = str(to_date - datetime.now())
    if '.' in diff:
        diff = diff[:diff.index('.')]
    return diff


def get_user_dir(bot, chat_id):
    """Gets the directory for 'chat_id' and creates it if necessary."""
    directory = os.path.join(bot.username, str(chat_id))
    os.makedirs(directory, exist_ok=True)
    return directory


def queue_message(job_queue, due, chat_id, reminder_file):
    """Queues a message reminder on 'job_queue' which will be
       sent on 'due' at the specified 'chat_id', reading and
       deleting the given 'reminder_file' after sent.
    """
    context = {
        'chat_id': chat_id,
        'reminder_file': reminder_file
    }
    job_queue.run_once(notify, due, context=context)


def create_reminder(bot, job_queue, chat_id, due, text):
    """Creates a reminder for 'chat_id' with the desired 'text'
       and queues its message, or does nothing if the quota exceeded.
    """
    if due is None:
        return  # Ignore

    directory = get_user_dir(bot, chat_id)
    if len(os.listdir(directory)) >= MAX_REMINDERS or \
            len(text.encode('utf-8')) > MAX_DATA_PER_REMINDER_BYTES:
        bot.send_message(chat_id, text='Quota exceeded. You cannot set more!')
        return

    if (due - datetime.now()) < timedelta(seconds=5):
        bot.send_message(chat_id, text="Uhm… that's pretty much right now cx")
        return

    out = os.path.join(directory, str(int(due.timestamp())))
    with open(out, 'w', encoding='utf-8') as f:
        f.write(text.strip())

    queue_message(job_queue, due, chat_id, reminder_file=out)
    diff = format_time_diff(due)
    bot.send_message(chat_id, text='I will remind you "{}" in {} :)'
                                   .format(text, diff))


def notify(bot, job):
    """Notifies by sending a message that a reminder due date is over"""
    chat_id = job.context['chat_id']
    reminder_file = job.context['reminder_file']

    with open(reminder_file) as f:
        text = f.read()

    if os.path.isfile(reminder_file):
        os.remove(job.context['reminder_file'])

    bot.send_message(chat_id, text=text if text else 'Time is over!')


def load_jobs(bot, job_queue):
    """Load all existing jobs (pending reminders) into the given
       'job_queue', and apologise if we missed any.
    """
    if not os.path.isdir(bot.username):
        return

    now = datetime.now()
    for chat_id in os.listdir(bot.username):
        apologise = False

        for reminder in os.listdir(get_user_dir(bot, chat_id)):
            reminder_file = os.path.join(bot.username, chat_id, reminder)
            reminder_date = datetime.fromtimestamp(int(reminder))

            if reminder_date > now:
                queue_message(job_queue, reminder_date,
                              int(chat_id), reminder_file)
            else:
                apologise = True
                os.remove(reminder_file)

        if apologise:
            bot.send_message(chat_id,
                text='Oops… looks like I missed some reminders. Sorry :(')


# Commands
def start(bot, update, job_queue):
    global inline_reminders
    try:
        ir = inline_reminders.pop(update.message.from_user.id)
        if not ir.remindin and not ir.remindat:
            raise ValueError()

        if ir.remindin and ir.remindat:
            update.message.reply_text(
                'Should I remind you "at" or "in"?',
                reply_markup=ReplyKeyboardMarkup(
                    [['At', 'In'], ['/cancel']], one_time_keyboard=True
                )
            )
            inline_reminders[update.message.from_user.id] = ir
            return 0  # 0 is the only conversation handler set
        else:
            due, text = ir.remindin if ir.remindin else ir.remindat
            create_reminder(bot, job_queue, update.message.chat_id, due, text)

    except (ValueError, KeyError) as e:
        update.message.reply_text(f'''
Hi! I'm {bot.first_name.title()} and running in "reminder" mode.

You can set reminders by using:
`/remindat 17:05 Optional text`
`/remindin    5m Optional text`

Or list those you have by using:
`/status`

Everyone is allowed to use {MAX_DATA_PER_REMINDER_BYTES / 1024}KB per reminder, and {MAX_REMINDERS} reminders max. No more!

Made with love by @Lonami and hosted by Richard ❤️
'''.strip(), parse_mode=ParseMode.MARKDOWN)

    return ConversationHandler.END


def restart(bot, update):
    if not from_admin(update):
        return

    import os
    import time
    import sys
    update.message.reply_text('Restarting {}…'.format(bot.first_name.title()))
    time.sleep(0.2)
    os.execl(sys.executable, sys.executable, *sys.argv)  


def clear(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    directory = get_user_dir(bot, chat_id)
    reminders = list(os.listdir(directory))
    if not reminders:
        update.message.reply_text('You have no reminders to clear dear :)')
        return

    if not args:
        update.message.reply_text(
            'Are you sure you want to clear {} reminders? Please type '
            '`/clear please` if you are totally sure!'
            .format(len(reminders)), parse_mode=ParseMode.MARKDOWN)
        return

    if args[0].lower() == 'please':
        for job in job_queue.jobs():
            if job.context['chat_id'] == chat_id:
                job.schedule_removal()

        for r in reminders:
            os.remove(os.path.join(directory, r))

        update.message.reply_text('You are now free! No more reminders :3')
    else:
        update.message.reply_text(
            '"{}" is not what I asked you to send xP'.format(args[0]))


def getremindin(text, update=None):
    """If 'update' is not None, the bot will reply.
       If the parsing succeeds, (due, text) will be returned.
       If the parsing fails, None will be returned.
    """
    m = REMINDIN_RE.search(text)
    if m is None:
        if update:
            update.message.reply_text(
                'Not sure what time you meant that to be! :s'
            )
        return

    if m.group(1):
        due = parsehour(m.group(1), reverse=True)

    elif m.group(2):
        due = float(m.group(2))
        unit = m.group(3)[0].lower() if m.group(3) else 'm'
        due *= {'s': 1,
                'm': 60,
                'h': 3600,
                'd': 86400}.get(unit, 60)

    else:
        if update:
            update.message.reply_text('Darn, my regex broke >.<')
        return

    due = datetime.now() + timedelta(seconds=due)
    text = text[m.end():].strip()
    return due, text


def remindin(bot, update, args, job_queue):
    if not args:
        update.message.reply_text('In when? :p')
        return

    r_in = getremindin(' '.join(args), update)
    if r_in:
        create_reminder(bot, job_queue, update.message.chat_id, r_in[0], r_in[1])


def getremindat(text, update=None):
    """If 'update' is not None, the bot will reply.
       If the parsing succeeds, (due, text) will be returned.
       If the parsing fails, (None, None) will be returned.
    """
    match = REMINDAT_RE.search(text)
    if match is None:
        if update:
            update.message.reply_text(
                'Not sure what time you meant that to be! :s'
            )
        return

    if match.group(1):
        due = parsehour(match.group(1), reverse=False)
        if match.group(2) is not None:  # PM
            due += 43200  # 12h * 60m * 60s

    else:
        if update:
            update.message.reply_text('Darn, my regex broke >.<')
        return

    m, s = divmod(due, 60)
    h, m = divmod(  m, 60)
    try:
        due = time(h, m, s)
        now = datetime.now()
        now_time = time(now.hour, now.minute, now.second)

        add_days = 1 if due < now_time else 0
        due = datetime(now.year, now.month, now.day + add_days,
                       due.hour, due.minute, due.second)

        text = text[match.end():].strip()
        return due, text
    except ValueError:
        if update:
            update.message.reply_text('Some values are out of bounds :o')
        return None


def remindat(bot, update, args, job_queue):
    if not args:
        update.message.reply_text('At what time? :p')
        return

    r_at = getremindat(' '.join(args), update)
    if r_at:
        create_reminder(bot, job_queue, update.message.chat_id, r_at[0], r_at[1])


def remindinline(bot, update):
    query = update.inline_query.query

    remindin = getremindin(query)
    remindat = getremindat(query)
    if remindin or remindat:
        global inline_reminders
        inline_reminders[update.inline_query.from_user.id] = \
            InlineReminder(remindin, remindat)
        update.inline_query.answer([],
                                   cache_time=0,
                                   switch_pm_text='Set reminder',
                                   switch_pm_parameter='stub')
    else:
        update.inline_query.answer([InlineQueryResultArticle(
            id=uuid4(),
            title='Time not recognised >.<',
            input_message_content=InputTextMessageContent(
                "Beep boop. Stub! I couldn't recognise the time you typed :S"
            )
        )])


def in_or_at(bot, update, job_queue):
    global inline_reminders
    text = update.message.text
    try:
        ir = inline_reminders.pop(update.message.from_user.id)
        if text == 'At':
            due, text = ir.remindat
            create_reminder(bot, job_queue, update.message.chat_id, due, text)
        elif text == 'In':
            due, text = ir.remindin
            create_reminder(bot, job_queue, update.message.chat_id, due, text)
        else:
            update.message.reply_text('Unknown option! Reminder forgotten >3<')

    except KeyError as e:
        update.message.reply_text(
            'I am really sorry, I forgot what your reminder was about :c'
        )

    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    update.message.reply_text('Remainder cancelled, changed your mind? ;)',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END



def status(bot, update):
    directory = get_user_dir(bot, update.message.chat_id)
    reminders = list(sorted(os.listdir(directory)))
    if not reminders:
        update.message.reply_text('You have no pending reminders. Hooray ^_^')
        return

    reminder = reminders[0]
    diff = format_time_diff(datetime.fromtimestamp(int(reminder)))

    with open(os.path.join(directory, reminder)) as f:
        text = f.read()

    text = ':\n' + text if text else '.'
    amount = ('{} reminders' if len(reminders) > 1 else '{} reminder')\
             .format(len(reminders))

    update.message.reply_text('{}. Next reminder in {}{}'
                              .format(amount, diff, text))


if __name__ == '__main__':
    with open('token', encoding='utf-8') as f:
        token = f.read().strip()
    updater = Updater(token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler(
        'restart', restart
    ))
    dp.add_handler(CommandHandler(
        'clear', clear, pass_args=True, pass_job_queue=True
    ))
    dp.add_handler(CommandHandler(
        'status', status
    ))
    dp.add_handler(CommandHandler(
        'remindin', remindin, pass_args=True, pass_job_queue=True
    ))
    dp.add_handler(CommandHandler(
        'remindat', remindat, pass_args=True, pass_job_queue=True
    ))
    dp.add_handler(InlineQueryHandler(
        remindinline
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler(
            # Start can start a normal conversation or via inline
            'start', start, pass_job_queue=True
        )],

        states={
            0: [RegexHandler('^(In|At)$', in_or_at, pass_job_queue=True)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    ))

    updater.bot.getMe()
    load_jobs(updater.bot, updater.job_queue)

    updater.start_polling()
    updater.idle()
