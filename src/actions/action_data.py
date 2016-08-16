
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

    def get_match_int(self, index, fallback=1):
        integer = self.match.group(index)
        if integer is None:  # No group captured, use fallback
            return fallback
        else:
            return NumberHelper.get_int(self.match.group(index))
