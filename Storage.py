import unittest
import re
from FileDouble import FileDouble
from OpenDouble import OpenDouble
from TimeDouble import TimeDouble
from Task import Task
from Pomo import Pomo

openDouble = OpenDouble()
if __name__ == '__main__':
    open = openDouble

class Storage:
    def __init__(self, time):
        self.tasks = []
        self.pomo = None
        self.time = time

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
            f.write("## Date Created: {:d}\n".format(int(task.date_created)))
            f.write("## Date Closed:")
            if task.date_closed != None:
                f.write(" {:d}\n".format(int(task.date_closed)))
            else:
                f.write("\n")
            f.write("## Summary\n")
            for line in task.summary.split("\n"):
                f.write(line + "\n")
            f.write("## Description\n")
            for line in task.description.split("\n"):
                f.write(line + "\n")

        if self.pomo:
            f.write("#### Pomodoro\n")
            remainingTimeFloat = self.pomo.get_remaining_time(self.time.time())
            f.write("## Time Remaining: {:f}\n".format(remainingTimeFloat))
            f.write("## Running: ")
            if self.pomo.is_paused():
                f.write("false\n")
            else:
                f.write("true\n")
                f.write("## Save Date: {:f}\n".format(int(self.time.time())))

        f.close()

    def load(self, filename):
        f = open(filename, 'r')
        state = 0
        newtask = None
        newpomo = None

        while True:
            line = f.readline()
            if line == "":
                break
            if state == 0:
                if re.match("#### Task", line):
                    newtask = Task("", "")
                    state = 1
                if re.match("#### Pomodoro", line):
                    newpomo = Pomo()
                    state = 7
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
                    state = 10
                else:
                    if blocked_reason is None:
                        blocked_reason = ""
                    blocked_reason += line
            elif state ==  10:
                mo = re.match("## Date Created: (.*)", line)
                if mo:
                    newtask.date_created = int(mo.group(1))
                    state = 11
            elif state == 11:
                mo = re.match("## Date Closed:(.*)", line)
                if mo:
                    if mo.group(1):
                        newtask.date_closed = int(mo.group(1))
                    state = 4
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
                if re.match("#### Task", line) or re.match("#### Pomodoro", line):
                    newtask.description = description.strip()
                    state = 0
                    self.tasks.append(newtask)
                    if re.match("#### Task", line):
                        state = 1
                        newtask = Task("", "")
                    else:
                        state = 7
                        newpomo = Pomo()
                else:
                    description += line
            elif state == 7:
                mo = re.match("## Time Remaining: (.*)", line)
                if mo:
                    remainingTime = float(mo.group(1))
                    newpomo.set_remaining_time(remainingTime)
                    self.pomo = newpomo
                    state = 8
            elif state == 8:
                mo = re.match("## Running: (.*)", line)
                if mo:
                    if mo.group(1) == "true":
                        state = 9
                    else:
                        state = 0
            elif state == 9:
                mo = re.match("## Save Date: (.*)", line)
                if mo:
                    saveDateUtc = float(mo.group(1))
                    elapsedSinceSave = self.time.time() - saveDateUtc
                    remainingTime = newpomo.get_remaining_time(self.time.time()) - elapsedSinceSave
                    newpomo.set_remaining_time( remainingTime if remainingTime > 0 else 0)
                    newpomo.start(self.time.time())
                    state = 0

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
## Date Created: 1000
## Date Closed:
## Summary
Task4
## Description
Task4Description word
multiline
#### Task
## State: Closed
## Blocked Reason
## Id: 7
## Date Created: 1001
## Date Closed: 1004
## Summary
Task7
## Description
Task7Description
#### Task
## State: Blocked
## Blocked Reason
BlockedReason
## Id: 8
## Date Created: 1002
## Date Closed:
## Summary
Task8
## Description
Task8Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(TimeDouble())
        self.assertTrue(storage.load('test_file'))
        self.assertTrue(fileDouble.is_closed())
        self.assertEqual('test_file', openDouble.filename[0])
        self.assertEqual('r', openDouble.mode[0])

        self.assertEqual(3, len(storage.tasks))

        self.assertEqual("Task4", storage.tasks[0].summary)
        self.assertEqual(4, storage.tasks[0].id)
        self.assertEqual("Task4Description word\nmultiline", storage.tasks[0].description)
        self.assertTrue(storage.tasks[0].is_open)
        self.assertEqual(1000, storage.tasks[0].date_created)
        self.assertIsNone(storage.tasks[0].date_closed)

        self.assertEqual("Task7", storage.tasks[1].summary)
        self.assertEqual(7, storage.tasks[1].id)
        self.assertEqual("Task7Description", storage.tasks[1].description)
        self.assertTrue(storage.tasks[1].is_closed)
        self.assertEqual(1001, storage.tasks[1].date_created)
        self.assertEqual(1004, storage.tasks[1].date_closed)

        self.assertEqual("Task8", storage.tasks[2].summary)
        self.assertEqual(8, storage.tasks[2].id)
        self.assertEqual("Task8Description", storage.tasks[2].description)
        self.assertTrue(storage.tasks[2].is_blocked)
        self.assertEqual("BlockedReason", storage.tasks[2].blocked_reason)
        self.assertEqual(1002, storage.tasks[2].date_created)
        self.assertIsNone(storage.tasks[0].date_closed)

    def test_load_invalid_datastore_missing_id(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Blocked Reason
## Date Created: 1000
## Date Closed:
## Summary
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(TimeDouble())
        self.assertFalse(storage.load('test_file'))

    def test_load_invalid_datastore_missing_summary(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Blocked Reason
## Id: 4
## Date Created: 1000
## Date Closed:
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(TimeDouble())
        self.assertFalse(storage.load('test_file'))

    def test_load_invalid_datastore_missing_description(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Blocked Reason
## Id: 4
## Date Created: 1000
## Date Closed:
## Summary
Task4
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(TimeDouble())
        self.assertFalse(storage.load('test_file'))

    def test_load_invalid_datastore_missing_state(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## Blocked Reason
## Id: 4
## Date Created: 1000
## Date Closed:
## Summary
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(TimeDouble())
        self.assertFalse(storage.load('test_file'))

    def test_load_invalid_datastore_missing_blocked_reason(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Id: 4
## Date Created: 1000
## Date Closed:
## Summary
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(TimeDouble())
        self.assertFalse(storage.load('test_file'))

    def test_load_missing_create_date(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Id: 4
## Blocked Reason
## Date Closed:
## Summary
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(TimeDouble())
        self.assertFalse(storage.load('test_file'))

    def test_load_missing_closed_date(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Id: 4
## Blocked Reason
## Date Created: 1000
## Summary
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(TimeDouble())
        self.assertFalse(storage.load('test_file'))


    def test_load_pomo(self):
        timeDouble = TimeDouble()

        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Pomodoro
## Time Remaining: 1001
## Running: false
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(timeDouble)
        self.assertTrue(storage.load('test_file'))

        self.assertTrue(storage.pomo.is_paused())
        self.assertEqual(1001, storage.pomo.get_remaining_time(timeDouble.time()))

    def test_load_task_and_pomo(self):
        timeDouble = TimeDouble()

        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Blocked
## Blocked Reason
BlockedReason
## Id: 8
## Date Created: 1000
## Date Closed:
## Summary
Task8
## Description
Task8Description
#### Pomodoro
## Time Remaining: 1001
## Running: false
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(timeDouble)
        self.assertTrue(storage.load('test_file'))

        self.assertEqual("Task8", storage.tasks[0].summary)
        self.assertEqual(8, storage.tasks[0].id)
        self.assertEqual("Task8Description", storage.tasks[0].description)
        self.assertTrue(storage.tasks[0].is_blocked)
        self.assertEqual("BlockedReason", storage.tasks[0].blocked_reason)

        self.assertTrue(storage.pomo.is_paused())
        self.assertEqual(1001, storage.pomo.get_remaining_time(timeDouble.time()))


    def test_load_running_pomo(self):
        timeDouble = TimeDouble()

        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Pomodoro
## Time Remaining: 100
## Running: true
## Save Date: 100
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(timeDouble)
        timeDouble.set_time(110)
        self.assertTrue(storage.load('test_file'))

        self.assertFalse(storage.pomo.is_paused())
        self.assertEqual(90, storage.pomo.get_remaining_time(timeDouble.time()))

class StorageTest_Save(unittest.TestCase):
    def setUp(self):
        None

    def test_save_tasks(self):
        storage = Storage(TimeDouble())

        task = Task("Task1", "Task1Description word\nMultiline", 10001)
        task.id = 1
        task.state = "Blocked"
        task.blocked_reason = "BlockedReason"
        storage.tasks.append(task)

        task = Task("Task2", "Task2Description", 10002)
        task.id = 2
        task.close(10003)
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
## Date Created: 10001
## Date Closed:
## Summary
Task1
## Description
Task1Description word
Multiline
#### Task
## State: Closed
## Blocked Reason
## Id: 2
## Date Created: 10002
## Date Closed: 10003
## Summary
Task2
## Description
Task2Description
""", fileDouble.written_data)

    def test_save_tasks_and_pomo(self):
        storage = Storage(TimeDouble())

        pomo = Pomo()
        storage.pomo = pomo

        task = Task("Task1", "Task1Description word\nMultiline", 1000)
        task.id = 1
        task.state = "Blocked"
        task.blocked_reason = "BlockedReason"
        storage.tasks.append(task)

        task = Task("Task2", "Task2Description", 1001)
        task.id = 2
        task.close(1002)
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
## Date Created: 1000
## Date Closed:
## Summary
Task1
## Description
Task1Description word
Multiline
#### Task
## State: Closed
## Blocked Reason
## Id: 2
## Date Created: 1001
## Date Closed: 1002
## Summary
Task2
## Description
Task2Description
#### Pomodoro
## Time Remaining: 1500.000000
## Running: false
""", fileDouble.written_data)

    def test_save_paused_pomo(self):
        timeDouble = TimeDouble()
        storage = Storage(timeDouble)

        pomo = Pomo()
        storage.pomo = pomo

        openDouble.reset()
        fileDouble = FileDouble()
        openDouble.add_file(fileDouble)

        storage.save('test_file')
        self.assertEqual('test_file', openDouble.filename[0])
        self.assertEqual('w+', openDouble.mode[0])
        self.assertEqual("""#### Pomodoro
## Time Remaining: 1500.000000
## Running: false
""", fileDouble.written_data)

    def test_save_running_pomo(self):
        timeDouble = TimeDouble()
        storage = Storage(timeDouble)

        pomo = Pomo()
        storage.pomo = pomo

        pomo.start(100.0)
        timeDouble.set_time(1000.2)

        openDouble.reset()
        fileDouble = FileDouble()
        openDouble.add_file(fileDouble)

        storage.save('test_file')
        self.assertEqual('test_file', openDouble.filename[0])
        self.assertEqual('w+', openDouble.mode[0])
        self.assertEqual("""#### Pomodoro
## Time Remaining: 599.800000
## Running: true
## Save Date: 1000.000000
""", fileDouble.written_data)

if __name__ == '__main__':
    unittest.main()
