from actions.action_base import ActionBase
from random import choice, randint


class HowOldAction(ActionBase):
    def __init__(self):
        super().__init__(name="ANSWER «HOW OLD?» QUESTIONS",
                         keywords=['how old'])

    def act(self, data):
        age = randint(2, 80)
        answers = ['{} years old', "around {} years old", '{}']
        self.send_msg(data, choice(answers).format(age))
