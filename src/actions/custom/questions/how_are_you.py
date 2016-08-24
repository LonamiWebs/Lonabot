from actions.action_base import ActionBase


class HowAreYouAction(ActionBase):
    def __init__(self):
        super().__init__(name="ANSWER «HOW ARE YOU?» QUESTIONS",
                         keywords=['how a?re? (yo)?u'])

        # Optional
        self.answers = ["i'm fine, thanks!", 'good ty', 'good thank you, wbu?', 'good!',
                        'feeling great :)', 'great', 'fine you?', 'alright',
                        "i'm okay, thanks, what about you?",
                        'Truth is that this is a random answer and does not represent how I feel.']
