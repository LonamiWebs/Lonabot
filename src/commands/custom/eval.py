from commands.command_base import CommandBase
from utils.safe_eval import *


class EvaluateAction(CommandBase):
    """Evaluates a mathematical expression"""
    def __init__(self):
        super().__init__(command='eval',
                         examples='/eval 5+2*(5-1)/2')

    def act(self, data):
        expression = data.parameter
        if '\n' in expression:
            self.send_msg(data, 'Sorry, new lines are not allowed.')
        else:
            try:
                if ',' in expression:
                    expression = expression.replace(',', '.')

                result = safe_eval_timeout(expression)
                self.send_msg(data, '{} = {}'.format(expression, result))

            except UnknownSymbol:  # i.e. max(1, 0)
                self.send_msg(data, "Sorry, I could not evaluate that.")

            except BadCompilingInput:  # i.e. 2**999999999999999999999**9999999999
                self.send_msg(data, 'That expression is too expensive to be evaluated.'
                              .format(data.ori_msg.sender.id))

            except TimeoutException:  # i.e. 2**999999999999999999999**9999999999 without checking compiling input
                self.send_msg(data, 'That expression is too expensive to be evaluated.')

            except ZeroDivisionError:  # i.e. 1 / 0
                self.send_msg(data, 'Anything divided by zero is not infinite.')

            except SyntaxError:  # i.e. empty string, new line attempt, lambdas or (((((((((((((((()
                self.send_msg(data, 'The expression is malformed.')

            except AssertionError as e:
                if data.sender.is_admin:
                    self.send_msg(data, 'An error occured: {}'.format(e))
                else:
                    self.send_msg(data, 'Sorry, an error occured.')
