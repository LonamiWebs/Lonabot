from actions.action_base import ActionBase


class RunPythonAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'RUN PYTHON CODE'

        # Admin command to run python code
        self.requires_admin = True
        self.set_keywords([r"^run\s((?:.|\n)+)"],
                          add_word_bounding=False,
                          replace_spaces_non_printable=False,
                          enable_multiline=True)

    def act(self, data):
        expression = data.match.group(1)
        print("'{}'".format(expression))
        exec(expression)
