from actions.action_base import ActionBase


class WhyAction(ActionBase):
    def __init__(self):
        super().__init__(name="ANSWER «WHY?» QUESTIONS",
                         keywords=['why+'])

        # Optional
        self.answers = ['cus i said so', "there's no real reason", 'you tell me',
                        'because im da boss', "because it's sunny", "coz i'm cool"]
