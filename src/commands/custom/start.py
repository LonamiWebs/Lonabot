from commands.command_base import CommandBase


class StartCommand(CommandBase):
    """Starts the bot"""

    def __init__(self):
        super().__init__(command='start',
                         examples=['/start'])

    def act(self, data):
        self.send_msg(data, 'Hello! Please send another command to get started.')
