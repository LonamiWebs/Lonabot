from actions.action import Action
from random import choice, randint

# Every action must be defined as follows:
# >>> def action(data):
# ...   data.send_msg(reply_text)
# ...
# The action may use the provided action data as it desires

# region Requests


def love(data):
    data.send_msg('love yo{} {}'.format('u' * randint(1, 10), '❤️' * randint(1, 5)))

# endregion

# region Friendly


def laugh(data):

    option = randint(0, 99)

    if option < 30:
        msg = ('x{}'.format('D' * randint(1, 4)))
    elif option < 60:
        msg = ('ha' * randint(2, 4))
    elif option < 70:
        msg = ('he' * randint(2, 3))
    elif option < 80:
        msg = ('lma{}'.format('o' * randint(1, 3)))
    elif option < 90:
        msg = ('l{}l'.format('o' * randint(1, 3)))
    elif option < 95:
        msg = ('L{}L'.format('O' * randint(6, 10)))
    else:
        msg = ('ROFLMAO!!')

    # 30% chance of adding exclamation marks
    if randint(0, 100) < 30:
        msg += '!' * randint(1, 5)

    data.send_msg(msg)


# endregion

# region Questions


def how_many(data):
    answers = ['erm... {}?', "i'd say {} but idk", 'clearly {}']
    data.send_msg(choice(answers).format(randint(0, 20)))


def how_long(data):
    if randint(0, 50) < 1:  # 1 out of 50 are exaggerated
        data.send_msg('{} years :D'.format(randint(100, 1000)))
        return

    minutes = randint(2, 300)
    hours, minutes = minutes // 60, minutes % 60
    if hours > 0:
        answers = ['{1} hours and {0} mins', "{1}h{0}m :)", 'i think... {1} hours and {0} mins?']
    else:
        answers = ['only {} mins!', "{} minutes", '{} mins']

    data.send_msg(choice(answers).format(minutes, hours))


def how_old(data):
    age = randint(2, 80)
    answers = ['{} years old', "around {} years old", '{}']
    data.send_msg(choice(answers).format(age))


def choose(data):
    choices = list(set(c for c in data.match.groups() if c != None))
    data.send_msg(choice(choices))


# endregion

# region Utils


def who_is(data):
    username = data.match.group(1)
    if username[0] == '@':  # Username
        data.send_msg('let me search it...')
        user = data.bot.user_db.get_user(username[1:])  # Skip the @
        if user is None:
            data.send_msg("sorry i don't know it")
        else:
            data.send_msg("got it! it's {} and its Telegram id is {}" \
                .format(user.name, user.id))

    else:  # Himself
        data.send_msg("you're {} (@{}) and your Telegram id is {}" \
            .format(data.sender.name, data.sender.username, data.sender.id))


def roll_dice(data):
    answers = ['rolling... {}!', "roll roll {}", '{}', '{} came', '{} came now']
    times = data.match.group(1)
    if times is not None:
        times = int(times)
    else:
        times = 1

    # Roll a dice n given times
    if times > 10:
        data.send_msg("i can't be bothered rolling it so many times")
    else:
        for _ in range(times):
            data.send_msg(choice(answers).format(randint(1, 6)))


# endregion

# region Admin


def get_users(data):
    data.send_msg('there are {} users online master'
                  .format(data.bot.user_db.user_count()))


# endregion

actions = [

    # region Hostile

    Action('INSULT',
           keywords=['screw u', 'screw you', '(yo)?u suck', 'sucka', 'idiot', 'stupid', 'asshole',
                     'bitch', 'whore', 'hoe', 'slut', 'rude', 'dumbass', 'f.?ck you', 'f u'],

           multiple_answers=[':(', 'hey dude calm.', 'why? 😭', 'YOU suck :)',
                             'well you bitch', 'pu-ta, you heard.', 'idiots...',
                             'not like i cared', 'idc', 'shut up please']),

    Action('HAS SPOKEN',
           keywords=['lobot has spoken'],
           multiple_answers=['yeh i did :D', "yup i'm god, deal with it",
                             'hehe i did', 'yuup!']),

    # endregion

    # region Hello and bye

    Action('HELLO',
           keywords=['hey+', 'hello+', 'hi+'],
           multiple_answers=['hey :D', 'hello', 'heyy', 'hi', 'welcome back']),

    Action('BYE',
           keywords=['bye', 'gtg', 'g2g', 'bye', 'cya', "i'm going", "i'm gonna", 'leaving'],
           multiple_answers=["don't go :(", 'bye', 'speak after!', 'cyaa', 'FINALLY LEAVING!!']),

    # endregion

    # region Thank

    Action('THANK',
           keywords=['ty+', 'thanks+', 'thank you+', 'thankyou+', 'thx'],
           multiple_answers=['np', 'np :)', 'no problem :D', 'no problem']),

    # endregion

    # region Friendly

    Action('COMPLIMENT',
           keywords=['love you+', 'ly+', 'cute+', 'swee+t', 'adorable', 'lovely',
                     "you're cool", 'you are coo+l', 'i like you'],
           multiple_answers=['shucks :$', "you'll make me blush", 'tyty',
                             "that's me, amazing", 'aww you too', 'you too :P',
                             'thanks for the compliment']),

    Action('LAUGH',
           keywords=["that's funny", 'so( much)? fun', 'lmao', 'lmfao',
                     'loo+l', 'a?ha+[ha]+', 'e?he+[he]+', 'xDD+'],
           action=laugh),

    # endregion

    # region Regret

    Action('REGRET',
           keywords=["i'?ll cry", "i'?m crying", 'that hurt', 'sad now', "i'?m sad"],
           multiple_answers=["i'm sorry", 'soz', "i didn't mean it",
                             'okay, i am sorry', 'soz man']),

    # endregion

    # region Questions

    Action('HOW MANY?',
           keywords=['how (many|much)'],
           action=how_many),

    Action('HOW LONG?',
           keywords=['how long'],
           action=how_long),

    Action('HOW OLD?',
           keywords=['how old'],
           action=how_old),

    Action('WHY?',
           keywords=['why+'],
           multiple_answers=['cus i said so', "there's no real reason", 'you tell me',
                             'im da boss', "because it's sunny", "coz i'm cool"]),

    Action('CHOOSE',
           keywords=['(\w+?)(?:,\s*(\w+?))* or (\w+?)',  # strings
                     '(\d+?)(?:,\s*(\d+?))* or (\d+?)'  # numbers
                    ],
           action=choose),

    # endregion

    # region Wasn't me

    Action("WASN'T ME",
           keywords=[r"(think |guess |maybe |perhaps )?he('s| is) .+? (us|me|them|they|s?he)"],
           multiple_answers=['no...', "wasn't me 👀", '*runs*',
                             'SMOKE BOMB!! 💣', 'nope, nope, nooopee, lies']),

    # endregion

    # region Environment

    Action('SOMEONE ANNOYED',
           keywords=[r'^\.\.\.+$'],
           multiple_answers=['someone is annoyed...', 'you ok?', "i think you are annoyed"],
           add_keyword_bounding=False
           ),

    # endregion

    # region Utils

    Action('LOVE',
           keywords=['gimme love', 'love me', 'wuv me', '<3 me'],
           action=love),

    Action('ROLL A DICE',
           keywords=[r'roll (?:a )?dice(?: (\d+) times?)?'],
           action=roll_dice),

    Action('WHO IS',
           keywords=['who (?:am|is) (i|me|@[a-zA-Z0-9_]+)'],
           action=who_is),

    # endregion

    # region Admin

    Action('GET USERS',
           keywords=['get users?'],
           action=get_users,
           requires_admin=True),

    # endregion

    # region Questions fall-back

    Action('QUESTION FALLBACK',
           keywords=[r'\w.*?\?!*$'],
           multiple_answers=[
               # Affirmative
               'yeh', 'sure', 'yes', 'yep!',
               'of course :D', 'that was obvious :)', 'haha yes', 'YES!!',
               'yee', 'yeah!', 'absolutely 😋', 'Affirmative.',

               # Negative
               'no', 'nah', 'nope', 'not quite',
               'HAHAHA no.', 'lol no', 'sadly no :(', 'in your dreams 😎',
               'not today', 'never', 'mayb... no', 'Negative.',

               # Unsure
               'well it depends :/', 'idno', 'maybe 😏', 'perhaps',

               # Avoiding the question
               'sorry i gotta go', 'idk right now', "i'm busy i'll answer l8r", 'why would you ask that?'
           ],
           add_keyword_bounding=False)

    # endregion
]
