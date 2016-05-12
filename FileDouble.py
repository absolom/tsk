
class FileDouble:
    def __init__(self):
        self.written_data = ""
        self.closed = False
        self.contents = None
        self.index = 0

    def write(self, data):
        self.written_data += data

    def is_closed(self):
        return self.closed

    def close(self):
        self.closed = True

    def set_contents(self, contents):
        self.contents = contents.split("\n")

    def readline(self):
        if not self.contents:
            return None
        if self.index < len(self.contents):
            ret = self.contents[self.index]
            self.index += 1
            return ret
        return None
