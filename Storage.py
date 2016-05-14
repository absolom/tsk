import unittest
import re
from FileDouble import FileDouble
from OpenDouble import OpenDouble
from Task import Task

openDouble = OpenDouble()
if __name__ == '__main__':
    open = openDouble

class Storage:
    def __init__(self):
        self.tasks = []

    def save(self, filename):
        f = open(filename, 'w+')
        for task in self.tasks:
            f.write("#### Task\n")
            f.write("## State: {:s}\n".format(task.state))
            f.write("## Blocked Reason\n")
            if task.blocked_reason:
                for line in task.blocked_reason.split("\n"):
                    f.write(line + "\n")
            f.write("## Id: {:d}\n".format(task.id))
            f.write("## Summary\n")
            for line in task.summary.split("\n"):
                f.write(line + "\n")
            f.write("## Description\n")
            for line in task.description.split("\n"):
                f.write(line + "\n")
        f.close()

    def load(self, filename):
        f = open(filename, 'r')
        state = 0
        newtask = None

        while True:
            line = f.readline()
            if line == "":
                break
            if state == 0:
                if re.match("#### Task", line):
                    newtask = Task("", "")
                    state = 1
            elif state == 1:
                mo = re.match("## State: (.*)", line)
                if mo:
                    newtask.state = mo.group(1)
                    state = 2
            elif state == 2:
                if re.match("## Blocked Reason", line):
                    blocked_reason = None
                    state = 3
            elif state == 3:
                mo = re.match("## Id: (.*)", line)
                if mo:
                    if blocked_reason:
                        newtask.blocked_reason = blocked_reason.strip()
                    newtask.id = int(mo.group(1))
                    state = 4
                else:
                    if blocked_reason is None:
                        blocked_reason = ""
                    blocked_reason += line
            elif state == 4:
                if re.match("## Summary", line):
                    summary = ""
                    state = 5
            elif state == 5:
                if re.match("## Description", line):
                    newtask.summary = summary.strip()
                    description = ""
                    state = 6
                else:
                    summary += line
            elif state == 6:
                if re.match("#### Task", line):
                    newtask.description = description.strip()
                    state = 0
                    self.tasks.append(newtask)
                    newtask = Task("", "")
                    state = 1
                else:
                    description += line

        if state == 6:
            newtask.description = description.strip()
            self.tasks.append(newtask)
            state = 0

        f.close()
        return state == 0

class StorageTest_Load(unittest.TestCase):
    def setUp(self):
        None

    def test_load(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Blocked Reason
## Id: 4
## Summary
Task4
## Description
Task4Description word
multiline
#### Task
## State: Closed
## Blocked Reason
## Id: 7
## Summary
Task7
## Description
Task7Description
#### Task
## State: Blocked
## Blocked Reason
BlockedReason
## Id: 8
## Summary
Task8
## Description
Task8Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage()
        self.assertTrue(storage.load('test_file'))
        self.assertTrue(fileDouble.is_closed())
        self.assertEqual('test_file', openDouble.filename[0])
        self.assertEqual('r', openDouble.mode[0])

        self.assertEqual(3, len(storage.tasks))

        self.assertEqual("Task4", storage.tasks[0].summary)
        self.assertEqual(4, storage.tasks[0].id)
        self.assertEqual("Task4Description word\nmultiline", storage.tasks[0].description)
        self.assertTrue(storage.tasks[0].is_open)

        self.assertEqual("Task7", storage.tasks[1].summary)
        self.assertEqual(7, storage.tasks[1].id)
        self.assertEqual("Task7Description", storage.tasks[1].description)
        self.assertTrue(storage.tasks[1].is_closed)

        self.assertEqual("Task8", storage.tasks[2].summary)
        self.assertEqual(8, storage.tasks[2].id)
        self.assertEqual("Task8Description", storage.tasks[2].description)
        self.assertTrue(storage.tasks[2].is_blocked)
        self.assertEqual("BlockedReason", storage.tasks[2].blocked_reason)

    def test_load_invalid_datastore_missing_id(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Blocked Reason
## Summary
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage()
        self.assertFalse(storage.load('test_file'))

    def test_load_invalid_datastore_missing_summary(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Blocked Reason
## Id: 4
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage()
        self.assertFalse(storage.load('test_file'))

    def test_load_invalid_datastore_missing_description(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Blocked Reason
## Id: 4
## Summary
Task4
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage()
        self.assertFalse(storage.load('test_file'))

    def test_load_invalid_datastore_missing_state(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## Id: 4
## Blocked Reason
## Summary
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage()
        self.assertFalse(storage.load('test_file'))

    def test_load_invalid_datastore_missing_blocked_reason(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Id: 4
## Summary
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage()
        self.assertFalse(storage.load('test_file'))

class StorageTest_Save(unittest.TestCase):
    def setUp(self):
        None

    def test_save(self):
        storage = Storage()

        task = Task("Task1", "Task1Description word\nMultiline")
        task.id = 1
        task.state = "Blocked"
        task.blocked_reason = "BlockedReason"
        storage.tasks.append(task)

        task = Task("Task2", "Task2Description")
        task.id = 2
        task.state = "Closed"
        storage.tasks.append(task)

        openDouble.reset()
        fileDouble = FileDouble()
        openDouble.add_file(fileDouble)

        storage.save('test_file')
        self.assertEqual('test_file', openDouble.filename[0])
        self.assertEqual('w+', openDouble.mode[0])
        self.assertEqual("""#### Task
## State: Blocked
## Blocked Reason
BlockedReason
## Id: 1
## Summary
Task1
## Description
Task1Description word
Multiline
#### Task
## State: Closed
## Blocked Reason
## Id: 2
## Summary
Task2
## Description
Task2Description
""", fileDouble.written_data)

if __name__ == '__main__':
    unittest.main()