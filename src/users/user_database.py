
class UserDatabase:
    """
    Represents an user database, which keeps track of all the users
    """

    def __init__(self):
        # Keep track of all the users which have talked to the bot in this instance
        self.loaded_users = []

    def check_user(self, user):
        """
        Checks an user in the database. If it's a new user, it's logged on console and adds it
        :param user: The user to check
        """
        if user not in self.loaded_users:
            print('A new user chatted with the bot: {}'.format(user))
            self.loaded_users.append(user)

    def get_user(self, username):
        """
        Retrieves a known user
        :param username: The username of the user
        :return: The user if found, None otherwise
        """
        for user in self.loaded_users:
            if user.username == username:
                return user

        return None

    def user_count(self):
        """
        Returns the currently logged user count
        """
        return len(self.loaded_users)
