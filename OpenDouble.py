
class OpenDouble:
    def __init__(self):
        self.filename = []
        self.mode = []
        self.file_double = []
        self.index = 0
        self.open_fail = False

    def reset(self):
        self.__init__()

    def add_file(self, file_double):
        self.file_double.append(file_double)

    def set_open_fail(self):
        self.open_fail = True

    def __call__(self, filename, mode):
        self.filename.append(filename)
        self.mode.append(mode)
        if self.open_fail:
            return None
        ret = self.file_double[self.index]
        self.index += 1
        return ret