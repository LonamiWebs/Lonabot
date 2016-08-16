from actions.action_base import ActionBase


class GetUsersAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'GET USERS'
        self.set_keywords(['get user?'])

        # Optional
        self.requires_admin = True

    def act(self, data):
        self.send_msg(data, 'there are {} users online master'
                      .format(data.bot.user_db.user_count()))
