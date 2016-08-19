from actions.action_base import ActionBase


class TellAction(ActionBase):
    def __init__(self):
        super().__init__(name="TELL SOMEONE SOMETHING",
                         keywords=[r'tell (\w+) to (.+)$'])

    def act(self, data):
        self.send_msg(data, '{}, {}'
                      .format(data.match.group(1), data.match.group(2)))
