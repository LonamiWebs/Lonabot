from actions.action_base import ActionBase


class DetectAnnoyedAction(ActionBase):
    def __init__(self):
        super().__init__(name="DETECT SOMEONE ANNOYED",
                         keywords=[r'\.\.\.+', 'gr+'],
                         keyword_match_whole_line=True,
                         answers=['someone is annoyed...', 'you ok?',
                                  'i think you are annoyed'])
