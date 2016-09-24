from pydoc import locate
from os import listdir, path
import inspect

from commands.command_base import CommandBase


def load_commands():
    # Store the found commands
    commands = []
    commands_dir = path.join('commands/custom')

    # Now list command files
    for command in listdir(commands_dir):
        if command.endswith('.py'):

            # We got a valid .py file
            command = command[:-3]  # Trim extension

            # Get full command path as a module path (not / but .)
            full_command = path.join(commands_dir, command).replace('/', '.')

            # Locate the module and iterate through the classes it contains
            module = locate(full_command)
            for name, obj in inspect.getmembers(module):

                # If it's a class AND subclasses CommandBase, we got our command!
                if (inspect.isclass(obj) and  # The object must be a class and
                            obj != CommandBase and  # It mustn't be the CommandBase and
                        issubclass(obj, CommandBase)):  # It has to inherit from it

                    commands.append(obj())

    return commands
