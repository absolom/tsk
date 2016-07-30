
class SubprocessDouble:
    def __init__(self):
        self.call_command = None
        self.vim_edits = None
        self.call_fail = False

    def call(self, command, shell=None):
        self.call_command = command
        self.call_shell = shell
        if self.call_fail:
            return 1
        return 0

    def set_call_fail(self):
        self.call_fail = True

class WriteDouble:
    def __init__(self):
        self.written_data = ""

    def __call__(self, ):
        self.filename = filename
        self.mode = mode
