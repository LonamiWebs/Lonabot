from actions.action_base import ActionBase


class ShutDownAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'SHUT DOWN'
        self.set_keywords(['shut( you)? (off|down)'])

        # Optional
        self.answers = ['okay, byee', 'okay master :)', 'cya soon everyone']
        self.requires_admin = True
