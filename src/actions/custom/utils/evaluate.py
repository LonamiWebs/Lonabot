from actions.action_base import ActionBase
from random import choice
from safe_eval import *


class EvaluateAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'EVALUATE A MATHEMATICAL EXPRESSION'

        # Evaluate anything which looks like a math expression (any digit and the operators)
        self.set_keywords([r"^(?:eval|evaluate|what is|what's)?([\d+-/*( )]+)"], add_word_bounding=False)

    def act(self, data):
        expression = data.match.group(1)
        if '\n' in expression:
            self.send_msg('no new line allowed')
        else:
            try:
                result = safe_eval_timeout(expression)
                self.send_msg(data, '{} = {}'.format(expression, result))

            except UnknownSymbol:  # i.e. max(1, 0)
                self.send_msg(data, "i don't know what you meant!")

            except BadCompilingInput:  # i.e. 2**999999999999999999999**9999999999
                self.send_msg(data, 'do that again and i will ban you, ID.{}'
                              .format(data.ori_msg.sender.id))

            except TimeoutException:  # i.e. 2**999999999999999999999**9999999999 without checking compiling input
                self.send_msg(data, 'what were you trying ID.{}?'.format(data.ori_msg.sender.id))

            except ZeroDivisionError:  # i.e. 1 / 0
                self.send_msg(data, choice([
                    'well yeah very funny trying to divide by zero :^)',
                    'that is not how maths work', '(anything / 0) is not infinite',
                    'why would you try to divide by 0 in the first place?']))

            except SyntaxError:  # i.e. empty string, new line attempt, lambdas or (((((((((((((((()
                self.send_msg(data, 'um... what did you mean?')

            except AssertionError:
                self.send_msg(data, 'something went really, really weird; do not do that or i will ban you')
