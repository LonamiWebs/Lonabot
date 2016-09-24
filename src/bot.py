import logging
import traceback
from datetime import datetime, timedelta
from os import path

import requests

from commands.command_list import load_commands
from tg_objects.message import Message
from tg_objects.user import User

# Bot name and username
name = 'Lobot'
username = 'lonabot'


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
        self.commands = load_commands()

        # We will only talk with our friends
        self.friends_path = '../Data/lonabot.friends'
        self.friends = {}
        self.load_friends()

        # The limit age after which we won't reply to a message
        self.msg_max_age = timedelta(minutes=1)

        print('{} has been initialized.'.format(name))

    # endregion

    # region Friends

    def load_friends(self):
        """Loads the friend list"""
        self.friends.clear()
        self.friends[User.admin_id] = 'Admin'
        if path.isfile(self.friends_path):
            with open(self.friends_path, 'r') as file:
                for line in file:
                    split = line.split('=')
                    friend_id = int(split[0])
                    friend_alias = split[1].strip()
                    self.friends[friend_id] = friend_alias

    def save_friends(self):
        """Saves the friend list"""
        with open(self.friends_path, 'w') as file:
            for friend_id, friend_alias in self.friends.items():
                file.write('{}={}\n'.format(friend_id, friend_alias))

    def add_friend(self, friend_id, friend_alias):
        """Adds a friend to the bot"""
        self.friends[friend_id] = friend_alias
        self.save_friends()

    def del_friend(self, friend_id):
        """Removes a friend from the bot, returning its alias"""
        if friend_id != User.admin_id and friend_id in self.friends:
            alias = self.friends[friend_id]
            del self.friends[friend_id]
            self.save_friends()

            return alias

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

        if len(text) > 4096:
            text = "Sorry, that message is too large to be sent."

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

    def send_audio(self, chat, file_handle=None, tg_id=None, title=None, artist=None):
        """
        Sends an audio file to the given chat

        :param chat: The chat to which the file will be sent
        :param file_handle: The file handle to the audio file that will be sent
        :param tg_id: If the audio was already uploaded, this can be provided not to upload it again
        :param title: The title of the song
        :param artist: The artist of the song

        :returns: The uploaded file Telegram ID (tg_id), which can be later used
        """
        parameters = {
            'chat_id': chat.id
        }
        if title is not None:
            parameters['title'] = title
        if artist is not None:
            parameters['performer'] = artist

        # If it was uploaded before, don't upload it again
        if tg_id is not None:
            parameters['audio'] = tg_id
            files = None

        else:  # Otherwise, set the files that we'll upload
            files = {'audio': file_handle}

        result = self.sendAudio(parameters, timeout=60, files=files)

        # Return the file ID if everything went okay
        if result['ok']:
            return result['result']['audio']['file_id']

    def send_photo(self, chat, file_handle=None, tg_id=None, caption=None):
        """
        Sends a photo file to the given chat

        :param chat: The chat to which the file will be sent
        :param file_handle: The file handle to the photo file that will be sent
        :param tg_id: If the photo was already uploaded, this can be provided not to upload it again
        :param caption: An optional caption for the photo

        :returns: The uploaded file Telegram ID (tg_id), which can be later used
        """
        parameters = {
            'chat_id': chat.id
        }
        if caption is not None:
            parameters['caption'] = caption

        # If it was uploaded before, don't upload it again
        if tg_id is not None:
            parameters['photo'] = tg_id
            files = None

        else:  # Otherwise, set the files that we'll upload
            # TODO Do not assume it's .jpg
            files = {'photo': ('photo.jpg', file_handle, 'image/jpeg')}

        result = self.sendPhoto(parameters, timeout=60, files=files)

        # Return the file ID if everything went okay
        if result['ok']:
            # -1 to return the largest (multiple sizes are returned)
            return result['result']['photo'][-1]['file_id']
        else:
            print(result)

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
        # We only want our friends
        if msg.sender.id not in self.friends:
            self.send_message(msg.chat,
                              text="Sorry {0}, but this is a _personal bot_ and you're not in my friend list. "
                              "Ask the *Admin* to issue the following command and you will be my friend:\n"
                              "`/friend add {1} {0}`"
                              .format(msg.sender.name, msg.sender.id),
                              markdown=True)

        elif msg.text is not None:
            # Check whether we should act
            for command in self.commands:
                should_act, data = command.should_act(self, msg, should_reply)
                if should_act:
                    self.act(msg, command, data)

    def act(self, msg, command, data):
        try:
            command.act(data)
        except Exception:
            # Something bad happened...
            if msg.sender.is_admin:
                self.send_message(msg.chat, 'An error occurred, admin:')
                self.send_message(msg.chat, traceback.format_exc())
            else:
                # TODO, this should be reported
                logging.error(traceback.format_exc())

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
        self.running = False

    # endregion

    # region Utils

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
