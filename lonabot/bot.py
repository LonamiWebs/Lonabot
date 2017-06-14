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
