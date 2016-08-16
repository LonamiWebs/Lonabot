from actions.action_base import ActionBase


class WasNotMeAction(ActionBase):
    def __init__(self):
        # Required
        self.name = "WASN'T ME"
        self.set_keywords([r"(think |guess |maybe |perhaps )?he .+? (us|me|them|they|s?he)"])

        # Optional
        self.answers = ['no...', "wasn't me 👀", '*runs*',
                        'SMOKE BOMB!! 💣', 'nope, nope, nooopee, lies']
