from actions.action_base import ActionBase


class HelloAction(ActionBase):
    def __init__(self):
        super().__init__(name="HELLO",
                         keywords=['hey+', 'hello+', 'hi+'],
                         answers=['hey :D', 'hello', 'heyy', 'hi', 'hey there', 'welcome back'])
