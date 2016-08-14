import requests, json
from interact import interact
from users.user import User


class Bot:

    def __init__(self, token):
        """
        Initializes the Telegram Bot with the given valid token.
        To get yours, please talk to @BotFather on Telegram.
        """
        self.token = token
        self.latest_update_id = 0  # So we can use it as an offset later

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
            url = 'https://api.telegram.org/bot' + self.token + '/' + method_name

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

        if ('message' in update and
                    'text' in update['message']):

            reply = {}
            reply['chat_id'] = update['message']['chat']['id']

            reply_to = User(update['message']['from'])
            for answer in interact(reply_to, update['message']['text']):
                reply['text'] = answer
                self.sendMessage(reply)
                print('Replying to @{} ({}): «{}» → «{}»'.format(
                    reply_to.username, reply_to.id,
                    update['message']['text'], answer))

    def run(self):
        """
        Runs the bot forever until it's stopped.
        Running the bot means it will continuously check for updates.
        """
        print('The bot is now running.')
        self.running = True
        while (self.running):
            self.check_updates()

    def stop(self):
        """
        Stops the bot.
        """
        self.running = False

    def print_json(self, jsonObj):
        """Useful debugging method to print a formatted JSON"""
        print(json.dumps(jsonObj, sort_keys=True, indent=2, separators=(',', ': ')))