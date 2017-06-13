from datetime import datetime, timedelta, time
from uuid import uuid4
import os

from telegram import (
    ParseMode, InlineQueryResultArticle, InputTextMessageContent,
    ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import ConversationHandler

from constants import *
from utilities import *
from inlinereminder import InlineReminder


def start(bot, update, job_queue):
    try:
        ir = InlineReminder.pop(update.message.from_user.id)
        if not ir.remindin and not ir.remindat:
            raise ValueError()

        if ir.remindin and ir.remindat:
            update.message.reply_text(
                'Should I remind you "at" or "in"?',
                reply_markup=ReplyKeyboardMarkup(
                    [['At', 'In'], ['/cancel']], one_time_keyboard=True
                )
            )
            InlineReminder.add(update.message.from_user.id, ir)
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
        InlineReminder.add(
            update.inline_query.from_user.id, InlineReminder(remindin, remindat)
        )
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
    text = update.message.text
    try:
        ir = InlineReminder.pop(update.message.from_user.id)
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