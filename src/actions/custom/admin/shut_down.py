from actions.action_base import ActionBase
from random import choice


class ShutDownAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'SHUT DOWN'
        self.set_keywords(['shut( you)? (off|down)', 'kill yourself',
                           'suicide', 'take your life away'])

        # Optional
        self.answers = ['okay, byee', 'okay master :)', 'cya soon everyone', 'x_x', '😲']
        self.requires_admin = True

    def act(self, data):
        self.send_msg(data, choice(self.answers))
        data.bot.stop()
