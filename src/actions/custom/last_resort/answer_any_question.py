from actions.action_base import ActionBase


class AnswerAnyQuestionAction(ActionBase):
    def __init__(self):
        super().__init__(name="ANSWER ANY QUESTION ENDING WITH «?»",
                         keywords=[r'\w.*?\?!*$'],
                         keyword_enhance_bounding=False,
                         answers=[
                                   # Affirmative
                                   'yeh', 'sure', 'yes', 'yep!',
                                   'of course :D', 'that was obvious :)', 'haha yes', 'YES!!',
                                   'yee', 'yeah!', 'absolutely 😋', 'Affirmative.',

                                   # Negative
                                   'no', 'nah', 'nope', 'not quite',
                                   'HAHAHA no.', 'lol no', 'sadly no :(', 'in your dreams 😎',
                                   'not today', 'never', 'mayb... no', 'Negative.',

                                   # Unsure
                                   'well it depends :/', 'idno', 'maybe 😏', 'perhaps',

                                   # Avoiding the question
                                   'sorry i gotta go', 'idk right now', "i'm busy i'll answer l8r", 'why would you ask that?'
                               ])

    def should_act(self, bot, msg, should_reply):
        # Do NOT trigger if 'what' is in the message, since it would make no sense
        # to answer a «What...» question with yes/no
        if 'what' in msg.text.lower():
            return False, None
        else:
            return super().should_act(bot, msg, should_reply)
