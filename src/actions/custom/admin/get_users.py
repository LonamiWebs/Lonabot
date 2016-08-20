from actions.action_base import ActionBase


class GetUsersAction(ActionBase):
    def __init__(self):
        super().__init__(name='GET USERS',
                         keywords=['get users?'],
                         requires_admin=True)

    def act(self, data):
        self.send_msg(data, '{} people have talked to me since i was started for the first time'
                      .format(data.bot.database.user_count()))
