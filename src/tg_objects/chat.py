
class Chat:
    """
    Represents a chat, which can be private or a group
    """
    def __init__(self, chat):
        """
        Initializes a chat instance
        :param chat: The dictionary containing the chat info
        """
        self.id = chat['id']
        self.type = chat['type']

        if self.type == 'private':
            self.name = chat['first_name']
            self.username = chat['username']
        else:
            self.name = chat['title']
