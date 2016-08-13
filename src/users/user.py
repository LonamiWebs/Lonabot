import pickle

class User:

    def __init__(self, user):
        self.id = user['id']
        self.name = user['first_name']
        self.username = user['username']


    def save(self):
        with open('entry.pickle', 'wb') as f:
            pickle.dump(self, f)
