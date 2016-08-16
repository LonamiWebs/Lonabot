from actions.action_base import ActionBase


class WhatCanBotDoAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'ANSWER «WHAT CAN YOU DO?» QUESTIONS'
        self.set_keywords(['what (can|do(es)?) (you|it|lobot) do'])

    def act(self, data):
        self.send_msg(data, 'with the right keywords, i can do many things:')
        self.send_msg(data, ', '.join(action.name.lower() for action in data.bot.actions
                                      if not getattr(action, 'requires_admin', False)))
