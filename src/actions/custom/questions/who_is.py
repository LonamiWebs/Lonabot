from actions.action_base import ActionBase
from random import choice
import re


class WhoIsAction(ActionBase):
    def __init__(self):
        super().__init__(name="ANSWER «WHO IS?» QUESTIONS",
                         keywords=['who (?:am|is|are|r) (u|you|lobot|@lonabot|i|me|@[a-zA-Z0-9_]+)'])

    def act(self, data):
        username = data.match.group(1)
        if username[0] == '@' and username != '@lonabot':  # Username
            self.send_msg(data, 'let me search it...')
            user = data.bot.database.get_user(username[1:])  # Skip the @
            if user is None:
                self.send_msg(data, "sorry i don't know it")
            else:
                self.send_msg(data, "got it! it's {} and its Telegram id is {}"
                                    .format(user.name, user.id))

        else:  # It may be the bot, or it may be the user who asked
            if re.match('(u|you|lobot|@lonabot)', username):
                answers = ["it's me :D", "i'm lobot", 'lobot they call me',
                           'ima bot', 'the best 😎', 'the person who fell in love with you ❤️',
                           "i'm lonami's kid", "i'm lonami's baby", "i'm lonami's mother"]

                self.send_msg(data, choice(answers))

            else:
                sender = data.ori_msg.sender
                self.send_msg(data, "you're {} (@{}) and your Telegram id is {}"
                                    .format(sender.name, sender.username, sender.id))
