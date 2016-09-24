from commands.command_base import CommandBase
import re


class HelpCommand(CommandBase):
    """Shows general help or help about a command"""

    def __init__(self):
        super().__init__(command='help',
                         examples=['/help', '/help command'])

    def act(self, data):
        if data.parameter:
            command_query = data.parameter
            command = next(c for c in data.bot.commands if c.command == command_query)
            if command:
                self.send_msg(data, command.long_description(), markdown=True)
            else:
                self.send_msg(data, "That command doesn't exist.")
        else:
            self.send_msg(data, 'Available commands:\n{}\n\n'
                                'Enter `/help command_name` for more information.'.format(
                '\n'.join(
                    '▸ {}'.format(c.small_description())
                    for c in data.bot.commands
                    if data.sender.is_admin or not c.requires_admin
                )
            ), markdown=True)
