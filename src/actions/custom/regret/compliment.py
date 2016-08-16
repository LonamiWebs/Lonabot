from actions.action_base import ActionBase


class RegretAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'REGRET'
        self.set_keywords(["i'?ll cry", "i'?m crying", 'that hurts?',
                           'sad now', "i'?m sad"])

        # Optional
        self.answers = ["i'm sorry", 'soz', "i didn't mean it",
                        'okay, i am sorry', 'soz man']
