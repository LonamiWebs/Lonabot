import random, re
from actions.action_data import ActionData


class ActionBase:
    """
    Defines an action (how the given bot will act to a message)
    """
    def __init__(self, name, keywords,
                 requires_admin=False, answers=[], enabled=True,
                 keyword_enhance_bounding=True,
                 keyword_enhance_spaces=True,
                 keyword_match_whole_line=False,
                 keyword_allow_emojis=False,
                 keyword_enable_multiline=False):
        """
        Initializes the action base
        :param name: The name of the action
        :param keywords: The keywords that will trigger this action

        :param requires_admin: Does the action require admin privileges?
        :param answers: How does the bot reply? This CANNOT be empty if «act(self, data)» is not overrode
        :param enabled: Is the action enabled? Some such as those that require tokens may not be

        :param keyword_enhance_bounding: Should word bounding «\bword\b» added to the keywords?
        :param keyword_enhance_spaces: Should the spaces be replaced with «\s*»?
        :param keyword_match_whole_line: Should the keyword match the whole line? This overrides bounding enhancement
        :param keyword_allow_emojis: Should the keyword allow emojis (enable unicode, may be slower)
        :param keyword_enable_multiline: Should the regex be able to match multiline strings?
        """
        # Set values which don't need to be enhanced
        self.name = name
        self.requires_admin = requires_admin
        self.answers = answers
        self.enabled = enabled

        # Set and enhance the keywords
        self.keywords = []
        for keyword in keywords:
            if keyword_match_whole_line:
                keyword = '^{}$'.format(keyword)
            elif keyword_enhance_bounding:
                keyword = r'\b{}\b'.format(keyword)

            if keyword_enhance_spaces:
                keyword = keyword.replace(' ', r'\s+')

            keyword = keyword.replace('INT', '(\d+|[\w\s-]+)')

            # Set the appropriated flags
            flags = 0
            flags |= re.IGNORECASE
            if keyword_enable_multiline:
                flags |= re.MULTILINE
            if keyword_allow_emojis:
                flags |= re.UNICODE

            self.keywords.append(re.compile(keyword, flags))

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
            return False, None  # We can't fire a non-enabled action

        if self.requires_admin and not msg.sender.is_admin:
            return False, None  # Early terminate, we won't act

        # See if we can match the sent text with any of this action's keywords
        match = None
        match_index = None
        for index, keyword in enumerate(self.keywords):
            match = keyword.search(msg.text)
            if match:
                match_index = index
                break  # Found a match, stop looking in the keywords

        if not match:
            return False, None  # No match found, don't act

        # Set the action data
        data = ActionData(bot, msg, match, match_index, should_reply)
        return True, data

    def act(self, data):
        """
        This method is the one to be override.
        By default, it sends one of the multiple_answers available

        :param data: The data available to the action
        """
        self.send_msg(data, random.choice(self.answers))

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

        print('Replied to @{} ({}): «{}» → «{}»'
              .format(data.ori_msg.sender.username, data.ori_msg.sender.id,
                      data.ori_msg.text, text))
