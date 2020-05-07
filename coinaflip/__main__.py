from dumbot import Bot
from . import bot


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    with open('coinaflip.token') as f:
        coinaflip = Bot(f.read().strip())
        bot.bot = coinaflip
        coinaflip.on_update = bot.on_update
        coinaflip.run()
