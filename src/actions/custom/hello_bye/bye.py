from actions.action_base import ActionBase


class ByeAction(ActionBase):
    def __init__(self):
        super().__init__(name="BYE",
                         keywords=['bye+', 'g[t2]g', 'cya+', "i'm going", 'leaving'],
                         answers=["don't go :(", 'bye', 'speak after!',
                                  'cyaa', 'goodbye', 'bye bye!', 'okay, byee'])
