import random, re
from actions.action_data import ActionData


class Action:
    """
    Defines an action (how the given bot will act to a message)
    """

    global bot

    def __init__(self, name, keywords, action=None, multiple_answers=[],
                 add_keyword_bounding=True, requires_admin=False):
        """
        Initializes this action
        :param name: The name of the action

        :param keywords: Which keywords trigger this action? They should be a valid regex

        :param action: The action to be triggered. If None, multiple_answers will be used

        :param multiple_answers: Returns one of the given multiple answers. This is mutually
                                 exclusive with action

        :param add_keyword_bounding: Should word bounding be added to the keywords?

        :param requires_admin: Determines whether the command is an admin-only command
        """
        self.name = name
        self.requires_admin = requires_admin

        # For each keyword, pre-compile the regex and optionally add word bounding
        self.keywords = []
        if add_keyword_bounding:
            for keyword in keywords:
                self.keywords.append(re.compile(r'\b{}\b'.format(keyword), re.IGNORECASE))
        else:
            for keyword in keywords:
                self.keywords.append(re.compile(keyword, re.IGNORECASE))

        # Set the action
        if action is not None:
            self.action = action  # If an action was provided, set it

        else:  # Else define a default action which replies with a random answer
            self.multiple_answers = multiple_answers

            def default_action(data):
                data.send_msg(random.choice(self.multiple_answers))

            self.action = default_action

    def act(self, bot, chat, user, text):
        """
        Acts if it should act with the given text. Otherwise, does nothing

        :param bot: The bot that will be used for the interaction
        :param chat: The chat where the reply will be sent back
        :param user: Who sent this message?
        :param text: The text message that the user sent
        :return: True if we acted; False otherwise
        """

        if self.requires_admin and not user.is_admin:
            return False  # Early terminate, we won't act

        # See if we can match the sent text with any of this action's keywords
        match = None
        for keyword in self.keywords:
            match = keyword.search(text)
            if match:
                break  # Found a match, stop looking in the keywords

        if not match:
            return False  # No match found, don't act

        # Set the action data
        data = ActionData(bot, chat, user, text, match)
        self.action(data)  # Fire the action
        return True
