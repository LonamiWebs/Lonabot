from actions.action_base import ActionBase


class DetectAnnoyedAction(ActionBase):
    def __init__(self):
        # Required
        self.name = "DETECT SOMEONE ANNOYED"
        self.set_keywords([r'^\.\.\.+$', '^gr+$'], add_word_bounding=False)

        # Optional
        self.answers = ['someone is annoyed...', 'you ok?',
                        "i think you are annoyed"]
