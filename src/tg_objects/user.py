class User:
    """
    Represents an user
    """
    def __init__(self, user):
        """
        Initializes an user instance
        :param user: Dictionary containing the user info or
                     4-tuple containing (id, name, last name, username)
        """

        if isinstance(user, dict):
            # Every user must have these values
            self.id = user['id']
            self.name = user['first_name']

            # These are optional
            self.username = user.get('username', None)
            self.last_name = user.get('last_name', None)

        elif isinstance(user, tuple):
            # If a tuple was given, it has to be a 4-tuple
            self.id = user[0]
            self.name = user[1]
            self.last_name = user[2]
            self.username = user[3]

        # Special case, our loved admin!
        self.is_admin = self.id == 10885151  # @Lonami

    # Override string representation
    def __str__(self):
        return '{} (@{}, id={})'.format(self.name, self.username, self.id)
