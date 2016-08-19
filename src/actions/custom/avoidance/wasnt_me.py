from actions.action_base import ActionBase


class WasNotMeAction(ActionBase):
    def __init__(self):
        super().__init__(name="WASN'T ME",
                         keywords=[r"(think |guess |maybe |perhaps )?he .+? (us|me|them|they|s?he)"],
                         answers=['no...', "wasn't me 👀", '*runs*',
                                  'SMOKE BOMB!! 💣', 'nope, nope, nooopee, lies'])
