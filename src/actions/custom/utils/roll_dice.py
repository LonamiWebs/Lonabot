from actions.action_base import ActionBase
from random import choice, randint


class RollDiceAction(ActionBase):
    def __init__(self):
        super().__init__(name="ROLL A DICE",
                         keywords=['roll (?:a )?dice(?: INT(?: times?)?)?',
                                   'roll INT dices?'])

    def act(self, data):
        answers = ['rolling... {}!', "roll roll {}", '{}', '{} came', '{} came now']
        times = data.get_match_int(1, fallback=1)

        # Roll a dice n given times
        if times > 100:
            self.send_msg(data, "{} are too many times, i'll do 100 though".format(times))
            times = 100

        if times == 1:  # Special message
            self.send_msg(data, choice(answers).format(randint(1, 6)))

        else:  # Else format it differently
            results = {}
            for i in range(1, 7):
                results[i] = 0  # Initialize 1..6 to 0

            for _ in range(times):
                rolled = randint(1, 6)
                results[rolled] += 1  # Count how many times a number came

            msg = ''
            for number, count in results.items():
                if count == 1:
                    msg += "{} came once\n".format(number)
                elif count == 2:
                    msg += "{} came twice\n".format(number)
                elif count != 0:  # Ignore 0 times case
                    msg += "{} came {} times\n".format(number, count)

            print(results)
            self.send_msg(data, msg.rstrip())
