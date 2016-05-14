import unittest
import re
from OpenDouble import OpenDouble
from FileDouble import FileDouble

openDouble = OpenDouble()
if __name__ == '__main__':
    open = openDouble

class TaskFileParser:
    def __init__(self):
        self.filename = None
        self.lines = []
        self.summary = None
        self.description = None

    def set_filename(self, filename):
        self.filename = filename

    def create_file(self, summary, description):
        f = open(self.filename, 'w+')
        if not f:
            return False
        f.write("#### Summary\n\n{:s}\n\n#### Description\n\n{:s}\n".format(summary, description))
        f.close()
        return True

    def load_file(self):
        f = open(self.filename, 'r')
        if not f:
            return False
        line = f.readline()
        while line != "":
            self.lines.append(line)
            line = f.readline()
        f.close()
        return True

    def parse(self):
        state = 0
        summary = []
        description = []

        for line in self.lines:
            if state == 0: # Waiting for #### Summary
                if re.match('#### Summary', line):
                    state = 1
            elif state == 1:
                if re.match('#### Description', line):
                    state = 2
                else:
                    summary.append(line)
            elif state == 2:
                description.append(line)

        self.summary = "".join(summary).strip()
        self.description = "".join(description).strip()

        return state == 2

class TaskFileParserTest(unittest.TestCase):
    def setUp(self):
        openDouble.reset()
        self.fileDouble = FileDouble()
        openDouble.add_file(self.fileDouble)
        self.tfp = TaskFileParser()
        self.tfp.set_filename('/tmp/tsk.tmp')
        self.fileDouble.set_contents("""#### Summary

Summary

#### Description

Description

""")

    def test_load_file_opens_correct_file(self):
        self.assertTrue(self.tfp.load_file())
        self.assertEquals('/tmp/tsk.tmp', openDouble.filename[0])
        self.assertEquals('r', openDouble.mode[0])

    def test_load_file_closes_file(self):
        self.tfp.load_file()
        self.assertTrue(self.fileDouble.is_closed())

    def test_load_file_fails(self):
        openDouble.set_open_fail()
        self.assertFalse(self.tfp.load_file())

    def test_parse(self):
        self.tfp.load_file()
        self.assertTrue(self.tfp.parse())

    def test_parse_unloaded(self):
        self.assertFalse(self.tfp.parse())

    def test_parse_strips(self):
        self.tfp.load_file()
        self.tfp.parse()
        self.assertEquals("Summary", self.tfp.summary)
        self.assertEquals("Description", self.tfp.description)

    def test_parse_fail_missing_summary(self):
        self.fileDouble.set_contents("""#### Description
Description
""")
        self.tfp.load_file()
        self.assertFalse(self.tfp.parse())


    def test_parse_fail_missing_description(self):
        self.fileDouble.set_contents("""#### Summary
Summary
""")
        self.tfp.load_file()
        self.assertFalse(self.tfp.parse())

    def test_create_file_fails(self):
        openDouble.set_open_fail()
        self.assertFalse(self.tfp.create_file("", ""))

    def test_create_file_opens_correct_file(self):
        self.tfp.create_file("", "")
        self.assertEquals("/tmp/tsk.tmp", openDouble.filename[0])
        self.assertEquals("w+", openDouble.mode[0])

    def test_create_file_closes_file(self):
        self.tfp.create_file("", "")
        self.assertTrue(self.fileDouble.is_closed())

    def test_create_file(self):
        self.assertTrue(self.tfp.create_file("Summary", "Description"))
        self.assertEquals("#### Summary\n\nSummary\n\n#### Description\n\nDescription\n", self.fileDouble.written_data)

if __name__ == '__main__':
    unittest.main()
