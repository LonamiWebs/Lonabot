class SchedReminder:
    def __init__(self, reminder_id, due):
        self.id = reminder_id
        self.due = due

    def __lt__(self, other):
        return self.due < other

    def __gt__(self, other):
        return self.due > other
