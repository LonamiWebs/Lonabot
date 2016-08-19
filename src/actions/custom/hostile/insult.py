from actions.action_base import ActionBase


class InsultAction(ActionBase):
    def __init__(self):
        super().__init__(name="INSULT",
                         keywords=['screw u', 'screw you', 'suck[as]*',
                                  'idiot', 'stupid', 'asshole', 'bitch', 'whore',
                                  'hoe', 'slut', 'rude', 'dumbass', 'f.?ck you', 'f u'],
                         answers=[':(', 'hey dude calm.', 'why? 😭', 'YOU suck :)',
                                  'well you bitch', 'pu-ta, you heard.', 'idiots...',
                                  'not like i cared', 'idc', 'shut up please'])

    def should_act(self, bot, msg, should_reply):
        # Only trigger if the name of the bot is in the message
        if 'lobot' in msg.text.lower():
            return super().should_act(bot, msg, should_reply)
        else:
            return False, None
