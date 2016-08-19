from actions.action_base import ActionBase
from random import choice, randint


class HowMany(ActionBase):
    def __init__(self):
        super().__init__(name="ANSWER «HOW MANY?» QUESTIONS",
                         keywords=['how (many|much)'])

    def act(self, data):
        answers = ['erm... {}?', "i'd say {} but idk", 'clearly {}']
        self.send_msg(data, choice(answers).format(randint(0, 20)))
