
from number_helper import NumberHelper


class ActionData:
    """
    Class describing all of the required data for an action to take place.
    """

    def __init__(self, bot, original_msg, match, should_reply):
        """
        :param bot: The bot to which we should act with this data
        :param original_msg: The original message (with sender, text, etc.)
        :param match: The found match when looking for keywords in an action
        :param should_reply: Hint that indicates whether this message should be a reply or not
        """
        self.bot = bot
        self.ori_msg = original_msg
        self.match = match
        self.should_reply = should_reply

    def send_msg(self, text, reply=False):
        """
        Shortcut function to send a message by using the bot provided in the action
        :param text: The text to be sent
        :param reply: Determines whether we're replying to the original message or not
        """

        if reply or self.should_reply:
            self.bot.send_message(self.ori_msg.chat, text, self.ori_msg.id)
        else:
            self.bot.send_message(self.ori_msg.chat, text)

        print('Replied to @{} ({}): «{}» → «{}»'
              .format(self.ori_msg.sender.username, self.ori_msg.sender.id,
                      self.ori_msg.text, text))

    def get_matched_int(self, index, fallback=1):
        integer = self.match.group(index)
        if integer is None:
            return fallback
        else:
            return NumberHelper.get_int(self.match.group(index))
