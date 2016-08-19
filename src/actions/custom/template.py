from actions.action_base import ActionBase


class ActionTemplate(ActionBase):
    def __init__(self):
        super().__init__(name='My Action',
                         keywords=['some', 'random', 'keywords'],
                         answers=['some', 'random', 'answers'],  # NOT optional if act(self, data) isn't overrode
                         requires_admin=False)

        # Apart from these, there are more parameters available

    '''
    # Optional. By default, act() picks a random answer.
    # It can be overrode to add a more customized functionality

    def act(self, data):
        self.send_msg(data, random.choice(self.answers))
    '''

"""
Notes:
1. The keywords should always be a valid regex. Furthermore:
     «INT» (without quotes) will be replaced for a regex to match
     an integer (or an integer literal), which can then be retrieved
     with data.get_match_int(index)
"""
