from actions.action_base import ActionBase

class MemeAction(ActionBase):
    def __init__(self):
        # Required
        self.name = 'SEND TEXT FACES'

        self.faces = {
            'lenny': '( ͡° ͜ʖ ͡°)',
            'shrug': '¯\_(ツ)_/¯',
            'sadface': 'ಠ╭╮ಠ',
            'strong': 'ᕦ(ò_óˇ,ᕤ',
            'deskflip': '(╯°□°）╯︵ ┻━┻',
            'happy': '^̮^',
            'happyy': '｡◕‿◕｡',
            'happyyy': '｡◕‿‿◕｡',
            'facepalm': '(>ლ)',
            'wink': 'ಠ‿↼',
            'gotya': '(☞ຈل͜ຈ)☞',
            'good one': '(☞ຈل͜ຈ)☞',
            'kawaii': '(~˘▾˘)~',
            'surprised': '◉_◉',
            'sing': '♪~ ᕕ(ᐛ)ᕗ',
            'mmm': '(づ￣ ³￣)づ',
            'gun': '▄︻̷̿┻̿═━一',
            'disapprove': 'ಠ_ಠ',
            'disapproval': 'ಠ_ಠ',
            'gross': 'ಠ_ಠ',
            'look': 'ಠ_ಠ'
        }

        # Join all the keywords together (as «face1|face2|...»)
        keywords = '({})$'.format('|'.join([key for key in self.faces]))
        self.set_keywords([keywords], add_word_bounding=False)

    def act(self, data):
        face = data.match.group(1)
        self.send_msg(data, self.faces[face])
