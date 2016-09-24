import random, re

import bot
from commands.command_data import CommandData


class CommandBase:
    """
    Defines an action (how the given bot will act to a message)
    """
    def __init__(self, command, examples,
                 enabled=True, requires_admin=False):
        # Set values which don't need to be enhanced
        self.command = command
        self.description = self.__doc__
        self.examples = examples

        self.enabled = enabled
        self.requires_admin = requires_admin

        # /command@botusername parameters
        #         ^ these parts being optional
        self.act_regex = re.compile(r'^/{}(?:@{})?(?: (.+))?$'
                                    .format(command, bot.username), flags=re.IGNORECASE)
        self.pending = {}  # Users with pending actions

    # region Pending state

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

    # endregion

    # region Description

    def small_description(self):
        return '/{} - _{}_'.format(self.command, self.description)

    def long_description(self):
        return ('*Name*: {}\n'
                '*Description*: _{}_\n\n'
                '*Examples*:\n{}'.format(self.__class__.__name__,
                                      self.description,
                                      '\n'.join(
                                          '▸ `{}`'.format(e)
                                          for e in self.examples)))

    # endregion

    # region Acting

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
        data = CommandData(bot=bot,
                           original_msg=msg,
                           parameter=match.group(1).strip() if match.group(1) else None,
                           should_reply=should_reply)

        return True, data

    def act(self, data):
        """
        This method is the one to be override.
        By default, it sends one of the multiple_answers available

        :param data: The data available to the action
        """
        raise NotImplementedError()

    # endregion

    # region Utilities

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

    def show_invalid_syntax(self, data):
        self.send_msg(data, 'The command syntax was invalid. See `/help {}` for more information.'
                      .format(self.command), markdown=True)

    # endregion
