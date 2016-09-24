from bot import Bot
from utils.tokens import load_token


if __name__ == "__main__":
    tg_token = load_token('TG')
    if tg_token is None:
        print('**The bot will not run**. Please make sure that you have read the full README.md!')
    else:
        bot = Bot('Lobot', load_token('TG'))
        bot.run()
