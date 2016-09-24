import random, re
from commands.command_data import CommandData


class CommandBase:
    """
    Defines an action (how the given bot will act to a message)
    """
    def __init__(self, command, examples,
                 takes_parameters=True, enabled=True, requires_admin=False):
        # Set values which don't need to be enhanced
        self.command = command
        self.description = self.__doc__
        self.examples = examples

        self.enabled = enabled
        self.requires_admin = requires_admin

        self.takes_parameters = takes_parameters
        if takes_parameters:
            self.act_regex = re.compile(r'^/{} (.+)$'.format(command), flags=re.IGNORECASE)
        else:
            self.act_regex = re.compile(r'^/{}$'.format(command), flags=re.IGNORECASE)

        self.pending = {}

    def set_pending(self, sender_id, data=None):
        """Sets the pending state"""
        self.pending[sender_id] = data

    def is_pending(self, sender_id):
        """Is the specified user pending?"""
        return sender_id in self.pending

    def get_pending(self, sender_id):
        """Gets the pending data and clears the pending state"""
        data = self.pending[sender_id]
        del self.pending[sender_id]
        return data

    def should_act(self, bot, msg, should_reply):
        """
        Determines whether the bot should act or not.
        If it should act, returns a second value containing the data for the action
        Acts if it should act with the given text. Otherwise, does nothing

        :param bot: The bot that will be used for the interaction
        :param msg: The sent message, with text, sender and where it belongs (which chat)
        :param should_reply: Hint that indicates whether the answer should reply to the original
                             message or not. This is useful when there are many messages between
                             the bot's answer and the original message

        :return: (True, ActionData) if we acted; (False, None) otherwise
        """
        if not self.enabled:
            return False, None

        if self.requires_admin and not msg.sender.is_admin:
            return False, None  # Early terminate, we won't act

        if self.is_pending(msg.sender.id):
            return True, CommandData(bot, msg, msg.text, should_reply)

        # See if we can match the sent text with any of this action's keywords
        match = self.act_regex.match(msg.text)
        if not match:
            return False, None  # No match found, don't act

        # Set the action data
        if self.takes_parameters:
            data = CommandData(bot, msg, match.group(1), should_reply)
        else:
            data = CommandData(bot, msg, None, should_reply)

        return True, data

    def act(self, data):
        """
        This method is the one to be override.
        By default, it sends one of the multiple_answers available

        :param data: The data available to the action
        """
        raise NotImplementedError()

    def send_msg(self, data, text, reply=False, markdown=False):
        """
        Shortcut function to send a message by using the bot provided in the action
        :param data: The data which is being used to act
        :param text: The text to be sent
        :param reply: Determines whether we're replying to the original message or not
        :param markdown: Should markdown format be used in this message?
        """
        if reply or data.should_reply:
            data.bot.send_message(data.ori_msg.chat, text, data.ori_msg.id, markdown=markdown)
        else:
            data.bot.send_message(data.ori_msg.chat, text, markdown=markdown)
