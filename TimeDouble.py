
class TimeDouble:
    def __init__(self):
        self.times = [0]
        self.index = 0

    def _getNextTime(self):
        if self.index < len(self.times):
            ret = self.times[self.index]
            self.index += 1
            return ret
        else:
            return self.times[-1]

    def set_time(self, t):
        self.times = [t]

    def add_time(self, t):
        self.times.append(t)

    def time(self):
        return self._getNextTime()

    def sleep(self, delta):
        self.times.append(self._getNextTime() + delta)
