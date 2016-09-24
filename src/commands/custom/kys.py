from commands.command_base import CommandBase


class KysCommand(CommandBase):
    """Kill YourSelf, bot"""

    def __init__(self):
        super().__init__(command='kys',
                         examples=['/kys'],
                         requires_admin=True)

    def act(self, data):
        self.send_msg(data, 'Shutting down.')
        data.bot.stop()
