
class TimeDouble:
    def __init__(self):
        self.saved_time = 0

    def set_time(self, t):
        self.saved_time = t

    def time(self):
        return self.saved_time
