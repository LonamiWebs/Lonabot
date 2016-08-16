from actions.action_base import ActionBase


class Test(ActionBase):
    def __init__(self):
        # Required
        self.name = 'Testing'
        self.set_keywords(['lobot test'])

        # Optional
        self.requires_admin = True
        self.answers = ['yes, sir']
