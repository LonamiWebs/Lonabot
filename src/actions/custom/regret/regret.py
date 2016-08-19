from actions.action_base import ActionBase


class RegretAction(ActionBase):
    def __init__(self):
        super().__init__(name="REGRET",
                         keywords=["i'?ll cry", "i'?m crying", 'that hurts?',
                                   'sad now', "i'?m sad"],
                         answers=["i'm sorry", 'soz', "i didn't mean it",
                                  'okay, i am sorry', 'soz man'])
