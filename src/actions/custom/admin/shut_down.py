from actions.action_base import ActionBase
from random import choice


class ShutDownAction(ActionBase):
    def __init__(self):
        super().__init__(name='SHUT DOWN',
                         keywords=['shut( you(rself)?)? ?(off|down)'],
                         keyword_enhance_spaces=False,
                         answers=['okay, byee', 'okay master :)', 'cya soon everyone', 'x_x', '😲'],
                         requires_admin=True)

    def act(self, data):
        self.send_msg(data, choice(self.answers))
        data.bot.stop()
