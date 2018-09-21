from dumbot import Bot
from . import bot


if __name__ == '__main__':
    with open('textobot.token') as f:
        textobot = Bot(f.read().strip())
        bot.bot = textobot
        textobot.on_update = bot.on_update
        textobot.run()
