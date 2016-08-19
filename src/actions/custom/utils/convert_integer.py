from actions.action_base import ActionBase


class ConvertIntegerAction(ActionBase):
    def __init__(self):
        super().__init__(name="CONVERT A LITERAL TO INTEGER",
                         keywords=['(?:convert )?INT to int(eger)?'])

    def act(self, data):
        self.send_msg(data, str(data.get_match_int(1)))
