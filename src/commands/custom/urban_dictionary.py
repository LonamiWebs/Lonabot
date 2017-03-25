from commands.command_base import CommandBase
import json
import requests
from random import randrange
from tempfile import TemporaryFile


class UrbanDictionaryCommand(CommandBase):
    """Defines a word or phrase as per the urban dictionary"""
    def __init__(self):
        super().__init__(command='ud',
                         examples=['/ud ayy lmao'])
        self.pats = []

    def act(self, data):
        if not data.parameter:
            self.show_invalid_syntax(data)
            return

        result = json.loads(requests.get('http://api.urbandictionary.com/v0/define?term='+data.parameter).text)
        if 'list' in result:
            definitions = result['list']
            if definitions:
                d = definitions[0]
                msg = '▸ *{}* ([see more]({}))\n\n{}\n\n_{}_'.format(
                    data.parameter, d['permalink'], d['definition'], d['example'])

                data.bot.send_message(data.chat, msg, markdown=True, disable_web_preview=True)
                return

        data.bot.send_message(data.chat, 'You speak a weird idiom.')
