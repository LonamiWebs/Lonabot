from pydoc import locate
from os import listdir, path
import inspect

from actions.action_base import ActionBase

# All the available action categories (folders)
action_categories = [
    # Highest priority
    '0testbed',
    'admin',
    'hostile',
    'hello_bye',
    'thank',
    'friendly',
    'regret',
    'questions',
    'avoidance',
    'environment',
    'utils',
    'last_resort'
    # Lowest priority
]


def load_actions():
    # Store the found actions here
    actions = []

    for category in action_categories:
        actions_dir = path.join('actions/custom', category)

        # Now list action files
        for action in listdir(actions_dir):
            if action.endswith('.py'):

                # We got a valid .py file
                action = action[:-3]  # Trim extension

                # Get full action path as a module path (not / but .)
                full_action = path.join(actions_dir, action).replace('/', '.')

                # Locate the module and iterate through the classes it contains
                module = locate(full_action)
                for name, obj in inspect.getmembers(module):

                    # If it's a class AND subclasses ActionBase, we got our action!
                    if (inspect.isclass(obj) and  # The object must be a class and
                                obj != ActionBase and  # It mustn't be the ActionBase and
                            issubclass(obj, ActionBase)):  # It has to inherit from it

                        actions.append(obj())

    return actions
