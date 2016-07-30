
class TskDouble:
    class TaskDouble:
        def __init__(self, summary, description):
            self.summary = summary
            self.description = description
            self.set_due_date_relative_offset = None

        def set_due_date(self, due_date_offset):
            self.set_due_date_relative_offset = due_date_offset
            return True

        def log_time(self, t):
            self.log_time_param = t

    def __init__(self):
        self.set_blocked_called = False
        self.set_blocked_reason = None
        self.set_blocked_id = None
        self.add_called = False
        self.add_summary = None
        self.add_description = None
        self.task = None
        self.get_task_id = None

    def set_blocked(self, id, reason):
        self.set_blocked_called = True
        self.set_blocked_id = id
        self.set_blocked_reason = reason
        return id == 10

    def add(self, summary, description=""):
        self.add_called = True
        self.add_summary = summary
        self.add_description = description
        self.task = self.TaskDouble(summary, description)
        return (True, 1)

    def set_active(self, id):
        return id == 10

    def set_open(self, id):
        return id == 10

    def set_closed(self, id, reason):
        return id == 10 and reason == "Reason"

    def get_task(self, id):
        self.get_task_id = id
        return self.task