from actions.action_base import ActionBase


class HasSpokenAction(ActionBase):
    def __init__(self):
        super().__init__(name="HAS SPOKEN",
                         keywords=['lobot has spoken'],
                         answers=['yeh i did :D', "yup i'm god, deal with it",
                                  'hehe i did', 'yuup!'])
