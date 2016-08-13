from actions.action import Action

from random import choice, randint


# Every action must be defined as follows:
#   def action(user, msg):
#     yield answer_n
#
# The answer *must* be iterable (by using yield, a list, a set, etc.)

def love(user, msg):
    yield ('love yo' +
           ('u' * randint(1, 10)) +
           ' ' +
           '❤️' * randint(1, 5))


def how_many(user, msg):
    answers = ['erm... {}?', "i'd say {} but idk", 'clearly {}']
    yield choice(answers).format(randint(0, 20))


def test_multiple(user, msg):
    yield 'multipl'
    yield 'multiple*'


actions = [

    Action('TEST MULTIPLE',
           keywords=['testing stuff'],
           action=test_multiple),

    Action('THANK',
           keywords=['ty', 'thanks', 'thank you', 'thankyou', 'thx'],
           multiple_answers=['np', 'np :)', 'no problem :D', 'no problem']),

    Action('LOVE',
           keywords=['gimme love', 'love me', 'wuv me', '<3 me'],
           action=love),

    Action('COMPLIMENT',
           keywords=['love you', 'ly', 'cute', 'sweet', 'adorable', 'lovely',
                     "you're cool", 'you are cool', 'i like you'],
           multiple_answers=['shucks :$', "you'll make me blush", 'tyty',
                             "that's me, amazing", 'aww you too', 'you too :P',
                             'thanks for the compliment']),

    Action('HELLO',
           keywords=['hey', 'hello', 'hi'],
           multiple_answers=['hey :D', 'hello', 'heyy', 'hi', 'welcome back']),

    Action('BYE',
           keywords=['bye', 'gtg', 'g2g', 'bye', 'cya', "i'm going", "i'm gonna", 'leaving'],
           multiple_answers=["don't go :(", 'bye', 'speak after!', 'cyaa', 'FINALLY LEAVING!!']),

    Action('HOW MANY?',
           keywords=['how many'],
           action=how_many),

    Action('INSULT',
           keywords=['screw u', 'screw you', 'u suck', 'sucka', 'idiot', 'stupid', 'asshole'
                     'bitch', 'whore', 'hoe', 'slut', 'dumbass'],

           multiple_answers=[':(', 'hey dude calm.', 'why? 😭', 'YOU suck :)',
                             'well you bitch', 'pu-ta, you heard.', 'idiots...',
                             'not like i cared', 'idc', 'shut up please'])
]
