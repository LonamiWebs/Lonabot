import requests, json
from actions.action_list import actions
from users.user_database import UserDatabase

from users.user import User
from chats.chat import Chat


class Bot:
    """
    Represents a Telegram bot
    """

    def __init__(self, token):
        """
        Initializes the Telegram Bot with the given valid token.
        To get yours, please talk to @BotFather on Telegram.
        """
        self.token = token
        self.latest_update_id = 0  # So we can use it as an offset later
        self.user_db = UserDatabase()

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
            for entry in result['result']:
                if entry['update_id'] > self.latest_update_id:

                    # Update the latest entry not to call it again
                    self.latest_update_id = entry['update_id']
                    self.on_update(entry)

    def on_update(self, update):
        """
        This method is called when there was an update available

        :param update: Dictionary containing all the update information
        """
        if 'message' in update and 'text' in update['message']:

            # Retrieve some information from the update
            chat = Chat(update['message']['chat'])
            user = User(update['message']['from'])
            text = update['message']['text']

            # Check the user in our database
            self.user_db.check_user(user)

            # Check whether we should act
            for action in actions:
                if action.act(self, chat, user, text):
                    break  # If we've acted, stop looking for interaction

    def send_message(self, chat, text):
        """
        Sends a message
        :param chat: The chat to where the message will be sent
        :param text: The text to be sent
        """
        self.sendMessage({
            'chat_id': chat.id,
            'text': text,
            'parse_mode': 'markdown'}
        )

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
            print('Exiting...')

    def stop(self):
        """
        Stops the bot.
        """
        self.running = False

    def print_json(self, jsonObj):
        """Useful debugging method to print a formatted JSON"""
        print(json.dumps(jsonObj, sort_keys=True, indent=2, separators=(',', ': ')))