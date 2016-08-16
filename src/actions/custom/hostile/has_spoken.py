from actions.action_base import ActionBase


class HasSpokenAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'HAS SPOKEN'
        self.set_keywords(['lobot has spoken'])

        # Optional
        self.answers = ['yeh i did :D', "yup i'm god, deal with it",
                        'hehe i did', 'yuup!']
