
class PomoDouble:
    def __init__(self):
        self.start_fail = False
        self.start_time = None
        self.pause_fail = False
        self.pause_time = None
        self.canceled = False
        self.cancel_fail = False
        self.monitor_count = 0

    def set_start_fail(self):
        self.start_fail = True

    def set_pause_fail(self):
        self.pause_fail = True

    def set_cancel_fail(self):
        self.cancel_fail = True

    def start(self, t):
        self.start_time = t
        return not self.start_fail

    def pause(self, t):
        self.pause_time = t
        return True

    def cancel(self):
        self.canceled = True
        return not self.cancel_fail

    def set_monitor_count(self, cnt):
        self.monitor_count = cnt

    def monitor(self, t):
        self.monitor_count -= 1
        return self.monitor_count > 0
