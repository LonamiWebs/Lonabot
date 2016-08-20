import json
import logging
import traceback
from datetime import datetime, timedelta

import requests
from database import Database

from actions.action_list import load_actions
from tg_objects.message import Message


class Bot:
    """
    Represents a Telegram bot
    """

    # region Initialization

    def __init__(self, name, token):
        """
        Initializes the Telegram Bot with the given valid token.
        To get yours, please talk to @BotFather on Telegram.
        """
        print('Initializing {}...'.format(name))

        self.name = name
        self.token = token
        self.latest_update_id = 0  # So we can use it as an offset later
        self.running = False
        self.actions = load_actions()

        # Set and load database
        self.database = Database()

        # The limit age after which we won't reply to a message
        self.msg_max_age = timedelta(minutes=1)

        print('{} has been initialized.'.format(name))

    # endregion

    # region Telegram API

    def __getattr__(self, method_name):
        """
        This method always return a callable function with optional parameters
        as argument, and a default timeout set to 5. This function calls the
        Telegram HTTP API.

        :param method_name: The Telegram method to call (i.e., getMe)
        :return: Dictionary containing the result. It always has an 'ok'
                 to check whether the request was OK
        """
        def request(parameters={}, timeout=5, files=None):
            url = 'https://api.telegram.org/bot{}/{}'.format(self.token, method_name)

            try:
                return requests.get(url, params=parameters, timeout=timeout, files=files).json()

            except requests.exceptions.ReadTimeout:
                return {'ok': False}

        return request

    # endregion

    # region Telegram API made easy

    def send_message(self, chat, text, reply_to_id=None, markdown=False):
        """
        Sends a message
        :param chat: The chat to where the message will be sent
        :param text: The text to be sent
        :param reply_to_id: To which message ID are we replying?
        :param markdown: Should the message use markdown formatting?
        """

        if len(text) > 1024:
            print('NOT SENDING MESSAGE: {}'.format(text))
            text = "the message i was gonna send is so long that i just gave up, hope that's ok :)"

        msg = {
            'chat_id': chat.id,
            'text': text
        }

        # Options
        if reply_to_id is not None:
            msg['reply_to_message_id'] = reply_to_id

        if markdown:
            msg['parse_mode'] = 'markdown'

        self.sendMessage(msg)

    def send_audio(self, chat, file_id, file_path=None, title=None, artist=None):
        """
        Sends an audio file to the given chat

        :param chat: The chat to which the file will be sent
        :param file_path: The path to the audio file that will be sent. May be None if file_id is provided.
        :param file_id: The ID of the file that will be sent
        :param tg_id: The ID of the file in the Telegram servers, not to re-upload the same file
        :param title: The title of the song
        :param artist: The artist of the song
        """
        parameters = {
            'chat_id': chat.id
        }
        if title is not None:
            parameters['title'] = title
        if artist is not None:
            parameters['performer'] = artist

        # First check if the file id is already on Telegram servers
        tg_id = self.database.check_file_audio(file_id)

        # If it was uploaded before, don't upload it again
        if tg_id is not None:
            parameters['audio'] = tg_id
            files=None

        else:  # Otherwise, set the files that we'll upload
            files = {'audio': open(file_path, 'rb')}

        result = self.sendAudio(parameters, timeout=60, files=files)

        # If we did upload the file for the first time, add it to the database
        if tg_id is None:
            files['audio'].close()  # Close the audio file if one was provided
            if result['ok']:
                tg_id = result['result']['audio']['file_id']
                self.database.add_file_audio(file_id, tg_id, title, artist)


    # endregion

    # region Updates

    def clear_updates(self):
        """
        This method sends a getUpdates request with the offset higher than the latest update,
        so this is not retrieved again (hence clearing the pending updates)
        """
        params = {
            'offset': self.latest_update_id + 1,  # Add +1 to avoid getting the previous update
            'timeout': 5
        }
        self.getUpdates(params, params['timeout'])

    def check_updates(self):
        """
        This method should constantly be called to check for Telegram updates.
        Updates happen when an user sent a message to the bot, a photo, etc.
        """
        params = {
            'offset': self.latest_update_id + 1,  # Add +1 to avoid getting the previous update
            'timeout': 300  # Arbitrarily large timeout for long polling
        }

        result = self.getUpdates(params, params['timeout'])

        if result['ok']:

            # Group the entries for easier use
            chat_id_msgs = self.group_entries(result['result'])

            # Now iterate over the messages per again
            for chat_id, msgs in chat_id_msgs.items():
                # If in this chat there were more than 1 message, reply instead only answer
                should_reply = len(msgs) > 1
                for msg in msgs:
                    self.on_update(msg, should_reply)

    def on_update(self, msg, should_reply):
        """
        This method is called when there was an update available
        :param msg: The message which was on the update
        :param should_reply: Hint that determines whether we should reply to it or just answer
        """

        if msg.text is not None:
            # Check the user in our database
            self.database.check_user(msg.sender)

            # Check whether we should act
            for action in self.actions:
                should_act, data = action.should_act(self, msg, should_reply)
                if should_act:
                    try:
                        action.act(data)
                    except Exception as e:
                        # Something baaad happened...
                        if msg.sender.is_admin:
                            self.send_message(msg.chat, 'oh, it was you admin, well here is the log:')
                            self.send_message(msg.chat, traceback.format_exc())
                        else:
                            # TODO, this should be reported
                            logging.error(traceback.format_exc())

                    break  # If we've acted, stop looking for interaction

    # endregion

    # region Running

    def run(self):
        """
        Runs the bot forever until it's stopped.
        Running the bot means it will continuously check for updates.
        """
        print('The bot is now running. Press Ctrl+C to exit.')
        self.running = True
        try:
            while self.running:
                self.check_updates()
        except KeyboardInterrupt:
            self.running = False
            print('Exiting...')

    def stop(self):
        """
        Stops the bot.
        """
        self.clear_updates()
        self.database.close()
        self.running = False

    # endregion

    # region Utils

    def print_json(self, json_obj):
        """Useful debugging method to print a formatted JSON"""
        print(json.dumps(json_obj, sort_keys=True, indent=2, separators=(',', ': ')))

    def group_entries(self, entries):
        """ This function groups entries from an update event into a dictionary
        containing {chat_id: msg_list} for easier use

        :param entries: The entries from an update's result
        :return: The grouped entries as {chat_id: msg_list}
        """
        chat_id_msgs = {}
        for entry in entries:
            if entry['update_id'] > self.latest_update_id:
                # Update the latest entry not to call it again
                self.latest_update_id = entry['update_id']

                if 'message' in entry:
                    # Retrieve some information from the update
                    msg = Message(entry['message'])

                    # If the message is not from a group, or is but also is
                    # younger than the limit age, we can add it
                    if (msg.chat.type != 'group' or
                                    datetime.now() - msg.date < self.msg_max_age):

                        if msg.chat.id in chat_id_msgs:
                            chat_id_msgs[msg.chat.id].append(msg)
                        else:
                            chat_id_msgs[msg.chat.id] = [msg]  # Initialize array

        return chat_id_msgs

    # endregion
