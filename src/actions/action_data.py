
class ActionData:
    """
    Class describing all of the required data for an action to take place.
    """

    def __init__(self, bot, chat, sender, original_msg, match):
        """
        :param bot: The bot to which we should act with this data
        :param chat: The chat to which we should act with this data
        :param sender: The original message sender
        :param original_msg: The original message text
        :param match: The found match when looking for keywords in an action
        """
        self.bot = bot
        self.chat = chat
        self.sender = sender
        self.original_msg = original_msg
        self.match = match

    def send_msg(self, text):
        """
        Shortcut function to send a message by using the bot provided in the action
        :param text: The text to be sent
        """

        self.bot.send_message(self.chat, text)
        print('Replied to @{} ({}): «{}» → «{}»'
              .format(self.sender.username, self.sender.id,
                      self.original_msg, text))