from commands.command_base import CommandBase


class PingCommand(CommandBase):
    """Pings the bot to check whether it's online or not"""
    def __init__(self):
        super().__init__(command='ping',
                         examples=['/ping'])

    def act(self, data):
        self.send_msg(data, 'Pong!')
