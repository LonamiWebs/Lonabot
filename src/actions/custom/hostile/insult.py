from actions.action_base import ActionBase


class InsultAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'INSULT'
        self.set_keywords(['screw u', 'screw you', '(yo)?u suck', 'sucka',
                           'idiot', 'stupid', 'asshole', 'bitch', 'whore',
                           'hoe', 'slut', 'rude', 'dumbass', 'f.?ck you', 'f u'])

        # Optional
        self.answers = [':(', 'hey dude calm.', 'why? 😭', 'YOU suck :)',
                        'well you bitch', 'pu-ta, you heard.', 'idiots...',
                        'not like i cared', 'idc', 'shut up please']
