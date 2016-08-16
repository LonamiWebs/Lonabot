from actions.action_base import ActionBase
from random import choice, randint


class HowLongAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'ANSWER «HOW LONG?» QUESTIONS'
        self.set_keywords(['how long'])

    def act(self, data):
        if randint(0, 50) < 1:  # 1 out of 50 are exaggerated
            self.send_msg(data, '{} years :D'.format(randint(100, 1000)))
            return

        minutes = randint(2, 300)
        hours, minutes = minutes // 60, minutes % 60
        if hours > 0:
            answers = ['{1} hours and {0} mins', "{1}h{0}m :)", 'i think... {1} hours and {0} mins?']
        else:
            answers = ['only {} mins!', "{} minutes", '{} mins']

        self.send_msg(data, choice(answers).format(minutes, hours))
