import random, re
from actions.action_data import ActionData


class Action:
    """
    Defines an action (how the given bot will act to a message)
    """

    def __init__(self, name, keywords, action=None, multiple_answers=[],
                 add_keyword_bounding=True, replace_spaces_nonprintable=True,
                 requires_admin=False):
        """
        Initializes this action
        :param name: The name of the action

        :param keywords: Which keywords trigger this action? They should be a valid regex.

                         «INT» (without quotes) will be replaced for a regex to match
                         an integer (or an integer literal), which can then be retrieved
                         with data.get_matched_int(index)

        :param action: The action to be triggered. If None, multiple_answers will be used

        :param multiple_answers: Returns one of the given multiple answers. This is mutually
                                 exclusive with action

        :param add_keyword_bounding: Should word bounding be added to the keywords?

        :param replace_spaces_nonprintable: Should spaces be replaced with \s+ (one or more spaces)?

        :param requires_admin: Determines whether the command is an admin-only command
        """
        self.name = name
        self.requires_admin = requires_admin

        # For each keyword, pre-compile the regex and optionally enhance it
        self.keywords = []
        for keyword in keywords:
            # Enhance the keyword
            if add_keyword_bounding:
                keyword = r'\b{}\b'.format(keyword)
            if replace_spaces_nonprintable:
                keyword = keyword.replace(' ', r'\s+')

            keyword = keyword.replace('INT', '(\d+|[\w\s-]+)')

            self.keywords.append(re.compile(keyword, re.IGNORECASE))

        # Set the action
        if action is not None:
            self.action = action  # If an action was provided, set it

        else:  # Else define a default action which replies with a random answer
            self.multiple_answers = multiple_answers

            def default_action(data):
                data.send_msg(random.choice(self.multiple_answers))

            self.action = default_action

    def act(self, bot, msg, should_reply):
        """
        Acts if it should act with the given text. Otherwise, does nothing

        :param bot: The bot that will be used for the interaction
        :param msg: The sent message, with text, sender and where it belongs (which chat)
        :param should_reply: Hint that indicates whether the answer should reply to the original
                             message or not. This is useful when there are many messages between
                             the bot's answer and the original message

        :return: True if we acted; False otherwise
        """

        if self.requires_admin and not msg.sender.is_admin:
            return False  # Early terminate, we won't act

        # See if we can match the sent text with any of this action's keywords
        match = None
        for keyword in self.keywords:
            match = keyword.search(msg.text)
            if match:
                break  # Found a match, stop looking in the keywords

        if not match:
            return False  # No match found, don't act

        # Set the action data
        data = ActionData(bot, msg, match, should_reply)
        self.action(data)  # Fire the action
        return True
