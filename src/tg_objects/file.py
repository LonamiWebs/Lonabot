
class File:
    def __init__(self, name, file_type, id=None):
        """
        Defines a sent file to the Telegram servers
        :param name: The name of the file
        :param file_type: The type of the file, i.e. «audio»
        :param id: The ID of the file in Telegram servers
        """
        self.name = name
        self.type = file_type
        self.id = id


    def __eq__(self, other):
        # Only check if the name AND the type is the same
        # i.e., «My song», «Audio»
        #
        # This way, we can look them up in a database without knowing the already uploaded ID
        # (and hence, retrieving that ID given a file)
        return (self.name == other.type and
                self.type == other.type)
