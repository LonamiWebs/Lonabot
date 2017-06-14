#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
#
import logging

from telegram.ext import (
    Updater, CommandHandler, InlineQueryHandler, MessageHandler, Filters,
    ConversationHandler, RegexHandler
)

from botcommands import *


if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    logger = logging.getLogger(__name__)

    with open('bot.token', encoding='utf-8') as f:
        token = f.read().strip()
    updater = Updater(token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler(
        'start', start
    ))
    dp.add_handler(InlineQueryHandler(
        formatinline
    ))
    dp.add_handler(MessageHandler(
        Filters.text, formatall
    ))

    updater.start_polling()
    updater.idle()
