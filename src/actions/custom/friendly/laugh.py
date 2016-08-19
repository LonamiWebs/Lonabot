from actions.action_base import ActionBase
from random import randint


class LaughAction(ActionBase):
    def __init__(self):
        super().__init__(name="LAUGH",
                         keywords=["that's funny", 'so( much)? fun', 'lmao+', 'lmfao+',
                                   'loo+l', 'a?ha+[ha]+', 'e?he+[he]+', 'xDD+'])

    def act(self, data):
        option = randint(0, 99)

        if option < 30:
            msg = ('x{}'.format('D' * randint(1, 4)))
        elif option < 60:
            msg = ('ha' * randint(2, 4))
        elif option < 70:
            msg = ('he' * randint(2, 3))
        elif option < 80:
            msg = ('lma{}'.format('o' * randint(1, 3)))
        elif option < 90:
            msg = ('l{}l'.format('o' * randint(1, 3)))
        elif option < 95:
            msg = ('L{}L'.format('O' * randint(6, 10)))
        else:
            msg = 'ROFLMAO!!'

        # 30% chance of adding exclamation marks
        if randint(0, 100) < 30:
            msg += '!' * randint(1, 5)

        self.send_msg(data, msg)
