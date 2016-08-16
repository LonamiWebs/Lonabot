from actions.action_base import ActionBase


class WhyAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'ANSWER «WHY?» QUESTIONS'
        self.set_keywords(['why+'])

        # Optional
        self.answers = ['cus i said so', "there's no real reason", 'you tell me',
                        'im da boss', "because it's sunny", "coz i'm cool"]
