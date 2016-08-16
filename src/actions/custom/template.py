from actions.action_base import ActionBase


class ActionTemplate(ActionBase):
    def __init__(self):
        # Required
        self.name = 'My Action'
        self.set_keywords(['some', 'random', 'keywords'])

        # Optional
        self.requires_admin = True

        # Note that this is NOT optional if act(self, data) isn't overrode
        self.answers = ['some', 'random', 'answers']

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
