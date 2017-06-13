from datetime import datetime, timedelta
import os

from constants import *
from inlinereminder import InlineReminder


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
    InlineReminder.cleanup()

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