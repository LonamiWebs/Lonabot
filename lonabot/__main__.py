from . import Lonabot, Database


if __name__ == '__main__':
    with open('lonabot.token') as f, Database('lonabot.db') as database:
        Lonabot(f.read().strip(), database).run()
