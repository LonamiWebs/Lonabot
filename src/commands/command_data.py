class CommandData:
    """
    Class describing all of the required data for an action to take place.
    """

    def __init__(self, bot, original_msg, parameter, should_reply):
        self.bot = bot
        self.ori_msg = original_msg
        self.parameter = parameter
        self.should_reply = should_reply

        # For faster access
        self.chat = original_msg.chat
        self.sender = original_msg.sender
