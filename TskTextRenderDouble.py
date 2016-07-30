
class TskTextRenderDouble:
    def __init__(self):
        self.get_active_string_called = False
        self.get_backlog_summary_string_called = False
        self.get_blocked_summary_string_called = False
        self.get_closed_summary_string_called = False
        self.get_active_string_response = ""
        self.get_backlog_summary_string_response = ""
        self.get_blocked_summary_string_response = ""
        self.get_closed_summary_string_response = ""
        self.set_backlog_max_max = []
        self.set_backlog_max_called = []
        self.set_closed_max_max = []
        self.set_closed_max_called = []

    def set_get_active_string_response(self, resp):
        self.get_active_string_response = resp

    def get_active_string(self):
        self.get_active_string_called = True
        return self.get_active_string_response

    def set_get_backlog_summary_string_response(self, resp):
        self.get_backlog_summary_string_response = resp

    def get_backlog_summary_string(self):
        self.get_backlog_summary_string_called = True
        return self.get_backlog_summary_string_response

    def set_get_blocked_summary_string_response(self, resp):
        self.get_blocked_summary_string_response = resp

    def get_blocked_summary_string(self):
        self.get_blocked_summary_string_called = True
        return self.get_blocked_summary_string_response

    def set_get_closed_summary_string_response(self, resp):
        self.get_closed_summary_string_response = resp

    def get_closed_summary_string(self):
        self.get_closed_summary_string_called = True
        return self.get_closed_summary_string_response

    def set_backlog_max(self, max):
        self.set_backlog_max_called.append(True)
        self.set_backlog_max_max.append(max)

    def set_closed_max(self, max):
        self.set_closed_max_called.append(True)
        self.set_closed_max_max.append(max)