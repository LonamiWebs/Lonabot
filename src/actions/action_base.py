import random, re
from actions.action_data import ActionData


class ActionBase:
    """
    Defines an action (how the given bot will act to a message)
    """

    def set_keywords(self, keywords, add_word_bounding=True, replace_spaces_non_printable=True):
        """
        This method sets the keywords that trigger the action

        :param keywords: The keywords to be set (and enhanced)
        :param add_word_bounding: Should word bounding «\bword\b» added to the keywords?
        :param replace_spaces_non_printable: Should the spaces be replaced with «\s*»?
        """
        self.__check_overrode()

        self.keywords = []
        for keyword in keywords:
            if add_word_bounding:
                keyword = r'\b{}\b'.format(keyword)
            if replace_spaces_non_printable:
                keyword = keyword.replace(' ', r'\s+')

            keyword = keyword.replace('INT', '(\d+|[\w\s-]+)')

            self.keywords.append(re.compile(keyword, re.IGNORECASE))

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
        self.__check_overrode()

        # requires_admin may have not been defined (not set), default's to False
        requires_admin = getattr(self, 'requires_admin', False)
        if requires_admin and not msg.sender.is_admin:
            return False, None  # Early terminate, we won't act

        # See if we can match the sent text with any of this action's keywords
        match = None
        for keyword in self.keywords:
            match = keyword.search(msg.text)
            if match:
                break  # Found a match, stop looking in the keywords

        if not match:
            return False, None  # No match found, don't act

        # Set the action data
        data = ActionData(bot, msg, match, should_reply)
        return True, data

    def act(self, data):
        """
        This method is the one to be override.
        By default, it sends one of the multiple_answers available

        :param data: The data available to the action
        """
        self.__check_overrode()
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

    def __check_overrode(self):
        if not hasattr(self, 'name'):
            raise NotImplementedError('Make sure to override ActionBase and set the appropriated attributes')
