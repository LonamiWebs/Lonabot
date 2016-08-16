from actions.action_base import ActionBase


class DetectAnnoyedAction(ActionBase):
    def __init__(self):
        # Required
        self.name = "DETECT SOMEONE ANNOYED"
        self.set_keywords(['(69)'], add_word_bounding=False)

        # Optional
        self.answers = ['someone is annoyed...', 'you ok?',
                        "i think you are annoyed"]

    def act(self, data):
        msg = '{} 😏'.format(data.match.group(1))
        self.send_msg(data, msg, reply=True)
