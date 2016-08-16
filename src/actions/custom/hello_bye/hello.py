from actions.action_base import ActionBase


class HelloAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'HELLO'
        self.set_keywords(['hey+', 'hello+', 'hi+'])

        # Optional
        self.answers = ['hey :D', 'hello', 'heyy', 'hi', 'hey there', 'welcome back']
