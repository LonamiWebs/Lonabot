import pickle


class User:
    """
    Represents an user
    """

    def __init__(self, user):
        """
        Initializes an user instance
        :param user: The dictionary containing the user info
        """

        self.id = user['id']
        self.name = user['first_name']
        self.username = user['username']

        # Special case, our loved admin!
        self.is_admin = self.id == 10885151  # @Lonami

    def save(self):
        with open('{}.pickle'.format(self.id), 'wb') as f:
            pickle.dump(self, f)

    # Override equality methods
    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    # Override string representation
    def __str__(self):
        return '{} (@{}, id={})'.format(self.name, self.username, self.id)
