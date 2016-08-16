from actions.action_base import ActionBase
from random import choice


class ChooseAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'CHOOSE «X» OR «Y»'
        self.set_keywords(['(\w+?)(?:,\s*(\w+?))* or (\w+?)',  # Strings
                           '(\d+?)(?:,\s*(\d+?))* or (\d+?)'  # Numbers
                           ])

    def act(self, data):
        choices = list(set(c for c in data.match.groups() if c is not None))
        self.send_msg(data, choice(choices))
