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


def what_can_bot_do(data):
    data.send_msg('with the right keywords, i can do many things:')
    data.send_msg(', '.join(action.name.lower()
                            for action in actions if not action.requires_admin))


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
    times = data.get_matched_int(1, fallback=1)

    # Roll a dice n given times
    if times > 100:
        data.send_msg("{} are too many times, i'll do 100 though".format(times))
        times = 100

    if times == 1:  # Special message
        data.send_msg(choice(answers).format(randint(1, 6)))

    else:  # Else format it differently
        results = {}
        for i in range(1, 7):
            results[i] = 0  # Initialize 1..6 to 0

        for _ in range(times):
            rolled = randint(1, 6)
            results[rolled] += 1  # Count how many times a number came

        msg = ''
        for number, count in results.items():
            if count == 1:
                msg += "{} came once\n".format(number)
            elif count == 2:
                msg += "{} came twice\n".format(number)
            elif count != 0:  # Ignore 0 times case
                msg += "{} came {} times\n".format(number, count)

        print(results)
        data.send_msg(msg.rstrip())



def pick_card(data):

    times = data.get_matched_int(1, fallback=1)
    if times > 10:  # Avoid too many
        data.send_msg("{} are too many, i'll do 10 ok?".format(times))
        times = 10

    # Add unique choices until we have enough
    result = set()
    while len(result) < times:
        # Pick a random value
        value = randint(2, 14)
        if value == 11:
            value = 'jack'
        elif value == 12:
            value = 'queen'
        elif value == 13:
            value = 'king'
        elif value == 14:
            value = 'ace'

        # Add the random value with the choice
        result.add('{} {}'.format(choice(['♠️', '♣️', '♥️', '♦️']), value))

    data.send_msg('\n'.join(result))


def to_int(data):
    data.send_msg(data.get_matched_int(1))


# endregion

# region Admin


def get_users(data):
    data.send_msg('there are {} users online master'
                  .format(data.bot.user_db.user_count()))


# endregion

actions = [

    # region Admin

    Action('GET USERS',
           keywords=['get users?'],
           action=get_users,
           requires_admin=True),

    Action('SHUT DOWN',
           keywords=['shut( you)? (off|down)'],
           multiple_answers=['okay, byee', 'okay master :)', 'cya soon everyone'],
           requires_admin=True),

    # endregion

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
           multiple_answers=['hey :D', 'hello', 'heyy', 'hi', 'hey there', 'welcome back']),

    Action('BYE',
           keywords=['bye', 'gtg', 'g2g', 'bye', 'cya', "i'm going", "i'm gonna", 'leaving'],
           multiple_answers=["don't go :(", 'bye', 'speak after!', 'cyaa', 'goodbye', 'bye bye!']),

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

    Action('ANSWER «HOW MANY?» QUESTIONS',
           keywords=['how (many|much)'],
           action=how_many),

    Action('ANSWER «HOW LONG?» QUESTIONS',
           keywords=['how long'],
           action=how_long),

    Action('ANSWER «HOW OLD?» QUESTIONS',
           keywords=['how old'],
           action=how_old),

    Action('ANSWER «WHY?» QUESTIONS',
           keywords=['why+'],
           multiple_answers=['cus i said so', "there's no real reason", 'you tell me',
                             'im da boss', "because it's sunny", "coz i'm cool"]),

    Action('CHOOSE «X» OR «Y»',
           keywords=['(\w+?)(?:,\s*(\w+?))* or (\w+?)',  # Strings
                     '(\d+?)(?:,\s*(\d+?))* or (\d+?)'  # Numbers
                    ],
           action=choose),

    Action('ANSWER «WHAT CAN YOU DO?» QUESTIONS',
           keywords=['what (can|do) (you|it) do'],
           action=what_can_bot_do),

    Action('ANSWER «WHO IS?» QUESTIONS',
           keywords=['who (?:am|is) (i|me|@[a-zA-Z0-9_]+)'],
           action=who_is),

    # endregion

    # region Wasn't me

    Action("WASN'T ME",
           keywords=[r"(think |guess |maybe |perhaps )?he('s| is) .+? (us|me|them|they|s?he)"],
           multiple_answers=['no...', "wasn't me 👀", '*runs*',
                             'SMOKE BOMB!! 💣', 'nope, nope, nooopee, lies']),

    # endregion

    # region Environment

    Action('DETECT SOMEONE ANNOYED',
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
           keywords=[r'roll (?:a )?dice(?: INT(?: times?)?)?'],
           action=roll_dice),

    Action('PICK A CARD FROM THE DECK',
           keywords=[r'pick( a| INT)? cards?'],
           action=pick_card),

    Action('COVERT A LITERAL TO INTEGER',
           keywords=['INT to int(eger)?'],
           action=to_int),

    # endregion

    # region Questions fall-back

    Action('ANSWER ANY QUESTION ENDING WITH «?»',
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
