from commands.command_base import CommandBase
import re


class FriendCommand(CommandBase):
    """Manages the friends of the bot"""

    def __init__(self):
        super().__init__(command='friend',
                         examples=[
                             '/friend add 123456789 alias',
                             '/friend del 123456789',
                             '/friend list',
                             '/friend clear'
                         ],
                         requires_admin=True)

    def act(self, data):
        if not data.parameter:
            self.show_invalid_syntax(data)
            return

        match = re.match(r'add (\d+) (\w+)', data.parameter)
        if match:
            # Add friend
            friend_id = int(match.group(1))
            friend_alias = match.group(2)
            data.bot.add_friend(friend_id, friend_alias)
            self.send_msg(data, "I've added {} as my friend.".format(friend_id))
            return

        match = re.match(r'del (\d+)', data.parameter)
        if match:
            # Delete friend
            friend_id = int(match.group(1))
            alias = data.bot.del_friend(friend_id)
            if not alias:
                self.send_msg(data, 'That user was not my friend.')
            else:
                self.send_msg(data, "I've deleted {} from my friend list.".format(alias))
            return

        match = re.match(r'list', data.parameter)
        if match:
            # List friends
            strings = []
            for friend_id, friend_alias in data.bot.friends.items():
                strings.append('`ID={}` - {}'.format(str(friend_id).ljust(10), friend_alias))

            self.send_msg(data, 'These are all my {} friends:\n{}'
                                .format(len(data.bot.friends), '\n'.join(strings)), markdown=True)
            return

        match = re.match(r'clear', data.parameter)
        if match:
            # Clear all friends
            for friend_id in data.bot.friends.keys():
                data.bot.del_friend(friend_id)

            self.send_msg(data, "I've deleted all the friends from my friend list")
            return
