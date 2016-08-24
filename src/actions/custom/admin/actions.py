from actions.action_base import ActionBase


class ActionsAction(ActionBase):
    def __init__(self):
        super().__init__(name='ACTION UTILITIES',
                         keywords=['list action (.+)',
                                   r'enable (.+)',
                                   r'disable (.+)'],
                         keyword_match_whole_line=True,
                         requires_admin=True)

    def act(self, data):

        # First get the query
        query = data.match.group(1).lower()

        # Then determine what we'll do with it
        if data.match_index == 0:  # List actions
            if query == '*' or query == 'all':
                query = None  # Match all actions

            self.send_msg(data,
                          markdown=True,
                          text='\n'.join('`[{}]` {}- {}'
                                         .format(str(index).ljust(2), '✅' if action.enabled else '❌', action.name.lower())
                                         for index, action in enumerate(data.bot.actions)
                                         if not query or query in action.name.lower()))

        # Enable or disable actions
        else:
            enabled = data.match_index == 1  # match_index 2 = disable

            # The query may be a name or an integer for which action we should toggle
            try:
                query = int(query)
                # It was an integer, only toggle that action
                action = data.bot.actions[query]

                if action.requires_admin:
                    self.send_msg(data, '{} is an admin action, left untouched'.format(action.name))
                else:
                    if enabled:
                        # Try enabling the action by initializing it again (we may not succeed!)
                        action.__init__()
                        if action.enabled:
                            self.send_msg(data, '«{}» is now enabled'.format(action.name.lower()))
                        else:
                            self.send_msg(data, 'could not enable «{}», '
                                                'make sure you satisfy all the requisites (i.e. tokens)'.format(
                                                action.name.lower()))
                    else:
                        action.enabled = False
                        self.send_msg(data, '«{}» is now disabled'.format(action.name.lower()))

            except ValueError:
                # It was a query, find all the matching actions
                actions = set([action for action in data.bot.actions
                               if query in action.name.lower() and not action.requires_admin])

                if len(actions) == 0:
                    self.send_msg(data, 'there were no actions matching that query')

                elif enabled:
                    # Store here the actions that we successfully enabled
                    enabled_actions = set()
                    for action in actions:
                        action.__init__()
                        if action.enabled:
                            enabled_actions.add(action)

                    # Notify depending on if all actions were enabled, or if some failed
                    if len(enabled_actions) == len(actions):
                        self.send_msg(data, 'all {} action(s) were enabled {}'
                                      .format(len(actions), self.get_actions_name(actions)))
                    else:
                        not_enabled = actions - enabled_actions
                        self.send_msg(data, '{} action(s) were enabled successfully {}\n\n'
                                            '{} action(s) failed to be enabled {}'
                                      .format(len(enabled_actions), self.get_actions_name(enabled_actions),
                                              len(not_enabled), self.get_actions_name(not_enabled)))
                else:
                    for action in actions:
                        action.enabled = False

                    self.send_msg(data, '{} action(s) were disabled: {}'
                                  .format(len(actions), ', '.join([action.name.lower() for action in actions])))

    def get_actions_name(self, actions):
        return '({})'.format(', '.join([action.name.lower() for action in actions]))
