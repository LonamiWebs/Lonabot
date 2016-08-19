from actions.action_base import ActionBase


class WhatCanBotDoAction(ActionBase):
    def __init__(self):
        super().__init__(name="ANSWER «WHAT CAN YOU DO?» QUESTIONS",
                         keywords=['what (can|do(es)?) (you|it|lobot) do'])

    def act(self, data):
        self.send_msg(data, 'with the right keywords, i can do many things:')
        self.send_msg(data, ', '.join(action.name.lower() for action in data.bot.actions
                                      if action.enabled and not action.requires_admin))
