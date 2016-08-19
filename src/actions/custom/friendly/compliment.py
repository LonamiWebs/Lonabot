from actions.action_base import ActionBase


class ComplimentAction(ActionBase):
    def __init__(self):

        keywords = ['cute+', 'swee+t', 'adorable', 'lovely', "coo+l", 'like']
        # Enhance the keywords by adding "is or are" to avoid things like "you're NOT cool"
        for i in range(len(keywords)):
            keywords[i] = "([i']s|[a']re) {}".format(keywords[i])

        super().__init__(name="COMPLIMENT",
                         keywords=keywords,
                         answers=['shucks :$', "you'll make me blush", 'tyty',
                                  "that's me, amazing", 'aww you too', 'you too :P',
                                  'thanks for the compliment'])

    def should_act(self, bot, msg, should_reply):
        # Only trigger if the name of the bot is in the message
        if 'lobot' in msg.text.lower():
            return super().should_act(bot, msg, should_reply)
        else:
            return False, None
