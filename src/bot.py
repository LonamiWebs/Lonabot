import requests, json
from actions.action_list import actions
from users.user_database import UserDatabase

from messages.message import Message


class Bot:
    """
    Represents a Telegram bot
    """

    def __init__(self, name, token):
        """
        Initializes the Telegram Bot with the given valid token.
        To get yours, please talk to @BotFather on Telegram.
        """
        self.name
        self.token = token
        self.latest_update_id = 0  # So we can use it as an offset later
        self.user_db = UserDatabase()
        self.running = False

    def __getattr__(self, method_name):
        """
        This method always return a callable function with optional parameters
        as argument, and a default timeout set to 5. This function calls the
        Telegram HTTP API.

        :param method_name: The Telegram method to call (i.e., getMe)
        :return: Dictionary containing the result. It always has an 'ok'
                 to check whether the request was OK
        """
        def request(parameters={}, timeout=5):
            url = 'https://api.telegram.org/bot{}/{}'.format(self.token, method_name)

            try:
                return requests.get(url, json=parameters, timeout=timeout).json()

            except requests.exceptions.ReadTimeout:
                return {'ok': False}

        return request

    def check_updates(self):
        """
        This method should constantly be called to check for Telegram updates.
        Updates happen when an user sent a message to the bot, a photo, etc.
        """
        params = {}
        params['offset'] = self.latest_update_id + 1  # Add +1 to avoid getting the previous update
        params['timeout'] = 300  # Arbitrarily large timeout for long polling

        result = self.getUpdates(params, params['timeout'])

        if result['ok']:

            # First iterate over all the updates and store them in a dictionary containing
            # chat: [msg updates], so we can later tell how many updates were in a chat.
            #
            # This will prove useful to determine whether we should reply to a message or if
            # it is not necessary (because the bot's reply will be next to the message to reply)
            chat_msgs = {}

            for entry in result['result']:
                if entry['update_id'] > self.latest_update_id:
                    # Update the latest entry not to call it again
                    self.latest_update_id = entry['update_id']

                    if 'message' in entry:
                        # Retrieve some information from the update
                        msg = Message(entry['message'])

                        if msg.chat.id in chat_msgs:
                            chat_msgs[msg.chat.id].append(msg)
                        else:
                            chat_msgs[msg.chat.id] = [msg]  # Initialize array

            # Now iterate over the messages per again
            for chat_id, msgs in chat_msgs.items():
                should_reply = len(msgs) > 1
                for msg in msgs:
                    self.on_update(msg, should_reply)

    def on_update(self, msg, should_reply):
        """
        This method is called when there was an update available

        :param update: Dictionary containing all the update information
        """

        if msg.text is not None:
            # Check the user in our database
            self.user_db.check_user(msg.sender)

            # Check whether we should act
            for action in actions:
                if action.act(self, msg, should_reply):
                    break  # If we've acted, stop looking for interaction

    def send_message(self, chat, text, reply_to_id=-1):
        """
        Sends a message
        :param chat: The chat to where the message will be sent
        :param text: The text to be sent
        """

        msg = {
            'chat_id': chat.id,
            'text': text}

        if reply_to_id != -1:  # Optional reply
            msg['reply_to_message_id'] = reply_to_id

        self.sendMessage(msg)

    def run(self):
        """
        Runs the bot forever until it's stopped.
        Running the bot means it will continuously check for updates.
        """
        print('The bot is now running. Press Ctrl+C to exit.')
        self.running = True
        try:
            while (self.running):
                self.check_updates()
        except KeyboardInterrupt:
            self.running = False
            print('Exiting...')

    def stop(self):
        """
        Stops the bot.
        """
        self.running = False

    def print_json(self, jsonObj):
        """Useful debugging method to print a formatted JSON"""
        print(json.dumps(jsonObj, sort_keys=True, indent=2, separators=(',', ': ')))