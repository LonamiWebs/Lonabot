from actions.action_base import ActionBase
from random import randint


class LoveAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'LOVE'
        self.set_keywords(['gimme love', 'love me', 'wuv me', '<3 me'])

    def act(self, data):
        self.send_msg(data, 'love yo{} {}'
                      .format('u' * randint(1, 10), '❤️' * randint(1, 5)))
