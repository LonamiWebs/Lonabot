from dumbot import Bot
from .bot import on_update


if __name__ == '__main__':
    with open('textobot.token') as f:
        bot = Bot(f.read().strip())
        bot.on_update = on_update
        bot.run()
