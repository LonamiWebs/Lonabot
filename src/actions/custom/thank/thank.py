from actions.action_base import ActionBase


class ThankAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'THANK'
        self.set_keywords(['ty+', 'thanks+', 'thank you+', 'thankyou+', 'thx'])

        # Optional
        self.answers = ['np', 'np :)', 'no problem :D', 'no problem']
