from commands.command_base import CommandBase
from utils.number_helper import NumberHelper


class ConvertCommand(CommandBase):
    """Converts string literals to integers"""

    def __init__(self):
        super().__init__(command='convert',
                         examples=[
                             '/convert twenty six',
                             '/convert one hundred and seven'
                         ])

    def act(self, data):
        self.send_msg(data, '{} = {}'
                      .format(data.parameter, NumberHelper.get_int(data.parameter)))
