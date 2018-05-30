import asyncio

from lonabot import Lonabot, Database

with open('lona.token') as f, Database('lonabot.db') as database:
    bot = Lonabot(f.read().strip(), database)
    asyncio.get_event_loop().run_until_complete(bot.start())
    asyncio.get_event_loop().run_forever()
