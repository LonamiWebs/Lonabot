from os.path import isfile


def load_token(name):
    """
    Loads a token file
    :param name: The name of the token, for example, «TG»
    :return: The token (or API key); None if it doesn't exist
    """
    file = '../Tokens/{}.token'.format(name)
    # Check that the file exists, otherwise return None
    if not isfile(file):
        return None

    with open(file, encoding='utf-8') as file:
        return file.readline().strip()