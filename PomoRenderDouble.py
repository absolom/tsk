

class PomoRenderDouble:
    def __init__(self):
        self.get_status_string_called = False
        self.get_status_string_response = ""

    def set_get_status_string_response(self, resp):
        self.get_status_string_response = resp

    def get_status_string(self, t):
        self.get_status_string_called = True
        return self.get_status_string_response
