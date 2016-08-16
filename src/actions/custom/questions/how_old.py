from actions.action_base import ActionBase
from random import choice, randint


class HowOldAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'ANSWER «HOW OLD?» QUESTIONS'
        self.set_keywords(['how old'])

    def act(self, data):
        age = randint(2, 80)
        answers = ['{} years old', "around {} years old", '{}']
        self.send_msg(data, choice(answers).format(age))
