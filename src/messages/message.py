
from users.user import User
from chats.chat import Chat


class Message:
    """
    Represents a message object
    """

    def __init__(self, msg):
        """
        Initializes a message instance
        :param msg: The dictionary containing the message info
        """

        self.id = msg['message_id']
        self.chat = Chat(msg['chat'])
        self.sender = User(msg['from'])

        if 'text' in msg:
            self.text = msg['text']
        else:
            self.text = None
