from actions.action_base import ActionBase


class ActionsAction(ActionBase):
    def __init__(self):
        super().__init__(name='ACTION UTILITIES',
                         keywords=['list actions',
                                   'list action (.+)',
                                   r'enable (\d+)',
                                   r'disable (\d+)'],
                         keyword_match_whole_line=True,
                         requires_admin=True)

    def act(self, data):
        print('oh')
        if data.match_index == 0:  # List
            self.send_msg(data, markdown=True, text='\n'.join('`[{}]` {}- {}'
                                          .format(str(index).ljust(2), '✅' if action.enabled else '❌', action.name.lower())
                                          for index, action in enumerate(data.bot.actions)))

        elif data.match_index == 1:  # List actions which match a query
            query = data.match.group(1)
            self.send_msg(data, markdown=True, text='\n'.join('`[{}]` {}- {}'
                                          .format(str(index).ljust(2), '✅' if action.enabled else '❌', action.name.lower())
                                          for index, action in enumerate(data.bot.actions)
                                          if query in action.name.lower()))

        elif data.match_index == 2:  # Enable
            idx = data.get_match_int(1)
            action = data.bot.actions[idx]
            if action.requires_admin:
                self.send_msg(data, '{} is an admin action, left untouched'.format(action.name))
            else:
                action.__init__()  # Re-initialize it
                if action.enabled:
                    self.send_msg(data, '{} is now enabled'.format(action.name))

                else:  # Notify that we couldn't enable it, fail on initialization
                    self.send_msg(data, 'could not enable {}, '
                                        'make sure you satisfy all the requisites (i.e. tokens)'.format(action.name))

        elif data.match_index == 3:  # Disable
            idx = data.get_match_int(1)
            action = data.bot.actions[idx]
            if action.requires_admin:
                self.send_msg(data, '{} is an admin action, left untouched'.format(action.name))
            else:
                action.enabled = False
                self.send_msg(data, '{} is now disabled'.format(action.name))
