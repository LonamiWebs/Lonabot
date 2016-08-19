from actions.action_base import ActionBase


class MemeAction(ActionBase):
    def __init__(self):
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
        keywords = ['({})'.format(kw) for kw in self.faces]
        super().__init__(name="SEND TEXT FACES",
                         keywords=keywords,
                         keyword_enhance_bounding=False)

    def act(self, data):
        face = data.match.group(1)
        self.send_msg(data, self.faces[face])
