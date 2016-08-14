from actions.action import Action
from random import choice, randint
from subprocess import check_output as run_command

# Every action must be defined as follows:
#   def action(user, msg, match):
#     yield answer_n
#
# The answer *must* be iterable (by using yield, a list, a set, etc.)

def love(user, msg, match):
    yield ('love yo' +
           ('u' * randint(1, 10)) +
           ' ' +
           '❤️' * randint(1, 5))


def how_many(user, msg, match):
    answers = ['erm... {}?', "i'd say {} but idk", 'clearly {}']
    yield choice(answers).format(randint(0, 20))


def how_long(user, msg, match):
    if randint(0, 50) < 1:  # 1 out of 50 are exaggerated
        yield '{} years :D'.format(randint(100, 1000))
        return

    minutes = randint(2, 300)
    hours, minutes = minutes // 60, minutes % 60
    if hours > 0:
        answers = ['{1} hours and {0} mins', "{1}h{0}m :)", 'i think... {1} hours and {0} mins?']
    else:
        answers = ['only {} mins!', "{} minutes", '{} mins']

    yield choice(answers).format(minutes, hours)


def how_old(user, msg, match):
    age = randint(2, 80)
    answers = ['{} years old', "around {} years old", '{}']
    yield choice(answers).format(age)


def who_am_i(user, msg, match):
    yield "you're {} (@{}) and your Telegram id is {}"\
        .format(user.name, user.username, user.id)


def execute(user, msg, match):
    try:
        output = str(run_command(match.group(1)), 'utf-8')
        yield output

    except FileNotFoundError:
        yield "i can't run that"


actions = [

    # region Debug

    Action('WHO AM I',
           keywords=['who am i'],
           action=who_am_i),

    # endregion

    # region Admin

    Action('EXECUTE',
           keywords=['(?:exec|execute|run) (.+?)'],
           action=execute,
           requires_admin=True),

    # endregion

    # region Hello and bye

    Action('HELLO',
           keywords=['hey+', 'hello+', 'hi+'],
           multiple_answers=['hey :D', 'hello', 'heyy', 'hi', 'welcome back']),

    Action('BYE',
           keywords=['bye', 'gtg', 'g2g', 'bye', 'cya', "i'm going", "i'm gonna", 'leaving'],
           multiple_answers=["don't go :(", 'bye', 'speak after!', 'cyaa', 'FINALLY LEAVING!!']),

    # endregion

    # region Requests

    Action('LOVE',
           keywords=['gimme love', 'love me', 'wuv me', '<3 me'],
           action=love),

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

    # endregion

    # region Regret

    Action('REGRET',
           keywords=["i'?ll cry", "i'?m crying", 'that hurt', 'sad now', "i'?m sad"],
           multiple_answers=["i'm sorry", 'soz', "i didn't mean it",
                             'okay, i am sorry', 'soz man']),

    # endregion

    # region Hostile

    Action('INSULT',
           keywords=['screw u', 'screw you', 'u suck', 'sucka', 'idiot', 'stupid', 'asshole'
                     'bitch', 'whore', 'hoe', 'slut', 'rude', 'dumbass'],

           multiple_answers=[':(', 'hey dude calm.', 'why? 😭', 'YOU suck :)',
                             'well you bitch', 'pu-ta, you heard.', 'idiots...',
                             'not like i cared', 'idc', 'shut up please']),

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

    # endregion

    # region Wasn't me

    Action("WASN'T ME",
           keywords=[r"(think |guess |maybe |perhaps )?he('s| is) .+? (us|me|them|they|s?he)"],
           multiple_answers=['no...', "wasn't me 👀", '*runs*',
                             'SMOKE BOMB!! 💣', 'nope, nope, nooopee, lies']),

    # endregion
]
