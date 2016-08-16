from actions.action_base import ActionBase


class TellAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'TELL SOMEONE SOMETHING'
        self.set_keywords([r'tell (\w+) to (.+)$'])

    def act(self, data):
        self.send_msg(data, '{}, {}'
                      .format(data.match.group(1), data.match.group(2)))
