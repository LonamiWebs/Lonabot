from commands.command_base import CommandBase
import json
import requests
from random import randrange
from tempfile import TemporaryFile


class PatCommand(CommandBase):
    """Head pat for the good little boy!"""
    def __init__(self):
        super().__init__(command='pat',
                         examples=['/pat'])
        self.pats = []

    def act(self, data):
        if not self.pats:
            self.pats = json.loads(requests.get('http://headp.at/js/pats.json').text)

        pat = 'http://headp.at/pats/' + self.pats.pop(randrange(len(self.pats)))

        with TemporaryFile() as handle:
            for chunk in requests.get(pat).iter_content(chunk_size=4096):
                handle.write(chunk)
            handle.seek(0)
            data.bot.send_photo(data.chat, file_handle=handle)
