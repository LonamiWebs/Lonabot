from actions.action_base import ActionBase


class NaughtyAction(ActionBase):
    def __init__(self):
        super().__init__(name="DETECT NAUGHTY",
                         keywords=['(69)'],
                         keyword_enhance_bounding=False)

    def act(self, data):
        msg = '{} 😏'.format(data.match.group(1))
        self.send_msg(data, msg, reply=True)
