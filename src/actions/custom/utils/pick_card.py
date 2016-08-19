from actions.action_base import ActionBase
from random import choice, randint


class PickCardAction(ActionBase):
    def __init__(self):
        super().__init__(name="PICK A CARD FROM THE DECK",
                         keywords=['pick a card (INT)',
                                   'pick (INT) cards?'])

    def act(self, data):
        times = data.get_match_int(1, fallback=1)
        if times > 48:  # Avoid too many
            self.send_msg(data,
                          "there are 48 cards in a deck (no joker here), "
                          "how am i supposed to pick {}?!".format(times))
            return

        if times == 48:
            self.send_msg(data, "there are 48 cards in the deck, BUT, if that makes you happy:".format(times))

        # Add unique choices until we have enough
        result = []
        while len(result) < times:
            # Pick a random value
            value = randint(2, 14)
            if value == 11:
                value = 'jack'
            elif value == 12:
                value = 'queen'
            elif value == 13:
                value = 'king'
            elif value == 14:
                value = 'ace'

            # And a random suit
            suit = choice(['♠️', '♣️', '♥️', '♦️'])
            current = '{}{}'.format(suit, value)

            # Add the random value with the choice if it wasn't in yet
            if current not in result:
                result.append(current)

        if times > 4:  # If too many times, let's make a pretty table!
            row_size = 4
            spacing = 7
            msg = '```\n'
            for i in range(0, times, row_size):

                # Join the results from i..i+row_size with a '.'
                msg += '.'.join(str(result[j]).ljust(spacing, '.')
                                for j in range(i, i + row_size) if j < times)
                msg += '\n'

            msg += '```'
            self.send_msg(data, msg, markdown=True)

        else:  # Else just join multiline
            self.send_msg(data, '\n'.join(result), markdown=True)

