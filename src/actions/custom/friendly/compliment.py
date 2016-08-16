from actions.action_base import ActionBase


class ComplimentAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'COMPLIMENT'
        self.set_keywords(['love you+', 'ly+', 'cute+', 'swee+t', 'adorable',
                           'lovely', "you're cool", 'you are coo+l', 'i like you'])

        # Optional
        self.answers = ['shucks :$', "you'll make me blush", 'tyty',
                        "that's me, amazing", 'aww you too', 'you too :P',
                        'thanks for the compliment']
