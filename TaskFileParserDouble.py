

class TaskFileParserDouble:
    def __init__(self):
        self.summary = None
        self.description = None
        self.set_filename_called = False
        self.create_file_called = False
        self.load_file_called = False
        self.parse_called = False
        self.set_filename_filename = None
        self.create_file_fail = False
        self.load_file_fail = False
        self.parse_fail = False

    def set_filename(self, filename):
        self.set_filename_called = True
        self.set_filename_filename = filename

    def create_file(self, summary, description):
        self.create_file_called = True
        self.create_file_summary = summary
        self.create_file_description = description
        return not self.create_file_fail

    def load_file(self):
        self.load_file_called = True
        return not self.load_file_fail

    def parse(self):
        self.parse_called = True
        return not self.parse_fail

    def set_summary(self, summary):
        self.summary = summary

    def set_description(self, description):
        self.description = description

    def set_create_file_fail(self):
        self.create_file_fail = True

    def set_load_file_fail(self):
        self.load_file_fail = True

    def set_parse_fail(self):
        self.parse_fail = True