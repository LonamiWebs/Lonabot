from actions.action_list import actions
from random import choice

question_answers = [
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
]


def interact(user, msg):
    """
    Returns an interaction message for the current message.

    :param user: The user who sent the message
    :param msg: The message
    :return: A set with the interaction answers, which may be empty
    """

    for action in actions:
        if action.should_trigger(msg):
            # Act will always return an iterable, convert it to a set
            return {a for a in action.act(user, msg)}

    if msg[-1] == '?':
        return {choice(question_answers)}

    return set()  # Empty (no answer)
