from datetime import datetime, timedelta, time
from itertools import chain
from uuid import uuid4
import os

from telegram import (
    ParseMode, InlineQueryResultArticle, InputTextMessageContent
)

from text import *


def start(bot, update):
    update.message.reply_text(f'''
Hi! I'm {bot.first_name.title()} and I will add fancy formats to your messages.

Just send a message and I will format it in every possible way that I know of.

Made with love by @Lonami and hosted by Richard ❤️
'''.strip(), parse_mode=ParseMode.MARKDOWN)


def formatinline(bot, update):
    query = update.inline_query.query
    update.inline_query.answer([
        InlineQueryResultArticle(
            id=uuid4(),
            title=t,
            input_message_content=InputTextMessageContent(itmc)
        ) for t, itmc in get_all(query) if itmc
    ])


def formatall(bot, update):
    text = update.message.text
    update.message.reply_text('\n\n'.join(t for _, t in get_all(text)))
