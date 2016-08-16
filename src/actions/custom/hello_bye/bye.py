from actions.action_base import ActionBase


class ByeAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'BYE'
        self.set_keywords(['bye', 'gtg', 'g2g', 'bye', 'cya',
                           "i'm going", "i'm gonna", 'leaving'])

        # Optional
        self.answers = ["don't go :(", 'bye', 'speak after!',
                        'cyaa', 'goodbye', 'bye bye!', 'okay, byee']
