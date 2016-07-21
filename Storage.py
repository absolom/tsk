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

class FileWrapper:
    def __init__(self, f):
        self.f = f
        self.rewindOn = False
        self.last_line = None

    def rewind(self):
        self.rewindOn = True

    def readline(self):
        ret = None

        if self.rewindOn and self.last_line is not None:
            ret = self.last_line
            self.rewindOn = False
        else:
            self.last_line = self.f.readline()
            ret = self.last_line

        return ret

    def close(self):
        self.f.close()

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
            f.write("## Closed Reason\n")
            if task.closed_reason:
                for line in task.closed_reason.split("\n"):
                    f.write(line + "\n")
            f.write("## Id: {:d}\n".format(task.id))
            f.write("## Date Created: {:d}\n".format(int(task.date_created)))
            f.write("## Date Closed:")
            if task.date_closed != None:
                f.write(" {:d}\n".format(int(task.date_closed)))
            else:
                f.write("\n")
            f.write("## Date Due:")
            if task.date_due is not None:
                f.write(" {:d}\n".format(int(task.date_due)))
            else:
                f.write("\n")

            f.write("## Pomo Estimate:")
            if task.pomo_estimate is not None:
                f.write(" {:d}\n".format(int(task.pomo_estimate)))
            else:
                f.write("\n")
            f.write("## Pomo Completed: {:d}\n".format(int(task.pomo_completed)))

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

    def _loadField(self, file, name, hasfield=False, multiline=False):
        line = file.readline()

        if line is None:
            return (False, None)

        if hasfield and not multiline:
                mo = re.match("## {:s}:(.*)".format(name), line)
                if mo:
                    ret = mo.group(1).strip()
                    if ret == '':
                        ret = None
                    return (True, ret)
                return (False, None)
        elif hasfield and multiline:
            mo = re.match("## {:s}".format(name), line)
            if not mo:
                return (False, None)
            ret = []
            while True:
                line = file.readline()
                if line is None:
                    if ret == []:
                        ret = None
                    return (True, ret)
                mo = re.match("##.*", line)
                if not mo:
                    ret.append(line)
                else:
                    file.rewind()
                    if ret == []:
                        ret = None
                    return (True, ret)
        else:
            mo = re.match("## {:s}".format(name), line)
            if mo:
                return (True, None)
            return (False, None)

# #### Task
# ## State: Open
# ## Blocked Reason
# ## Closed Reason
# ## Id: 4
# ## Date Created: 1000
# ## Date Closed:
# ## Date Due:
# ## Pomo Estimate:
# ## Pomo Completed: 0
# ## Summary
# Task4
# ## Description
# Task4Description word
# multiline

    def load(self, filename):
        f = open(filename, 'r')
        f = FileWrapper(f)
        state = "Start"
        newtask = None
        newpomo = None

        skip_read = False
        while True:
            if not skip_read:
                line = f.readline()
            skip_read = False
            if line == "":
                break
            if state == "Start":
                if re.match("#### Task", line):
                    newtask = Task("", "")
                    state = "Task_State"
                    skip_read = True
                if re.match("#### Pomodoro", line):
                    newpomo = Pomo()
                    state = "Pomo_Remaining"
            elif state == "Task_State":
                found, val = self._loadField(f, 'State')
                newtask.state = val
                state = "Task_BlockedReason"

            elif state == "Task_BlockedReason":
                found, val = self._loadField(f, 'Blocked Reason', hasfield=True, multiline=True)
                blocked_reason = None
                if val is not None:
                    blocked_reason = "\n".join(val)
                state = "Task_ClosedReason"
                # Left off here: Need to fix remaining failing test cases and replace parsing
                # machine with calls to _loadField()


                # if re.match("## Blocked Reason", line):
                #     blocked_reason = None
                #     state = "Task_ClosedReason"
            elif state == "Task_ClosedReason":
                mo = re.match("## Closed Reason", line)
                if mo:
                    if blocked_reason:
                        newtask.blocked_reason = blocked_reason.strip()
                    closed_reason = None
                    state = "Task_Id"
                else:
                    if blocked_reason is None:
                        blocked_reason = ""
                    blocked_reason += line
            elif state == "Task_Id":
                mo = re.match("## Id: (.*)", line)
                if mo:
                    if closed_reason:
                        newtask.closed_reason = closed_reason.strip()
                    newtask.id = int(mo.group(1))
                    state = "Task_DateCreated"
                else:
                    if closed_reason is None:
                        closed_reason = ""
                    closed_reason += line
            elif state ==  "Task_DateCreated":
                mo = re.match("## Date Created: (.*)", line)
                if mo:
                    newtask.date_created = int(mo.group(1))
                    state = "Task_DateClosed"
            elif state == "Task_DateClosed":
                mo = re.match("## Date Closed:(.*)", line)
                if mo:
                    if mo.group(1):
                        newtask.date_closed = int(mo.group(1))
                    state = "Task_DateDue"
            elif state == "Task_DateDue":
                mo = re.match("## Date Due:(.*)", line)
                if mo:
                    if mo.group(1):
                        newtask.date_due = int(mo.group(1))
                    state = "Task_PomoEstimate"
            elif state == "Task_PomoEstimate":
                mo = re.match("## Pomo Estimate:(.*)", line)
                if mo:
                    if mo.group(1):
                        newtask.pomo_estimate = int(mo.group(1))
                    state = "Task_PomoCompleted"
            elif state == "Task_PomoCompleted":
                mo = re.match("## Pomo Completed: (.*)", line)
                if mo:
                    newtask.pomo_completed = int(mo.group(1))
                    state = "Task_Summary"
            elif state == "Task_Summary":
                if re.match("## Summary", line):
                    summary = ""
                    state = "Task_Description"
            elif state == "Task_Description":
                if re.match("## Description", line):
                    newtask.summary = summary.strip()
                    description = ""
                    state = "End"
                else:
                    summary += line
            elif state == "End":
                if re.match("#### Task", line) or re.match("#### Pomodoro", line):
                    newtask.description = description.strip()
                    self.tasks.append(newtask)
                    if re.match("#### Task", line):
                        state = "Task_State"
                        skip_read = True
                        newtask = Task("", "")
                    else:
                        state = "Pomo_Remaining"
                        newpomo = Pomo()
                else:
                    description += line
            elif state == "Pomo_Remaining":
                mo = re.match("## Time Remaining: (.*)", line)
                if mo:
                    remainingTime = float(mo.group(1))
                    newpomo.set_remaining_time(remainingTime)
                    self.pomo = newpomo
                    state = "Pomo_Running"
            elif state == "Pomo_Running":
                mo = re.match("## Running: (.*)", line)
                if mo:
                    if mo.group(1) == "true":
                        state = "Pomo_SaveDate"
                    else:
                        state = "Start"
            elif state == "Pomo_SaveDate":
                mo = re.match("## Save Date: (.*)", line)
                if mo:
                    saveDateUtc = float(mo.group(1))
                    elapsedSinceSave = self.time.time() - saveDateUtc
                    remainingTime = newpomo.get_remaining_time(self.time.time()) - elapsedSinceSave
                    newpomo.set_remaining_time( remainingTime if remainingTime > 0 else 0)
                    newpomo.start(self.time.time())
                    state = "Start"

        if state == "End":
            newtask.description = description.strip()
            self.tasks.append(newtask)
            state = "Start"

        f.close()
        return state == "Start"

class StorageTest_Load(unittest.TestCase):
    def setUp(self):
        None


    def test_load(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Blocked Reason
## Closed Reason
## Id: 4
## Date Created: 1000
## Date Closed:
## Date Due:
## Pomo Estimate:
## Pomo Completed: 0
## Summary
Task4
## Description
Task4Description word
multiline
#### Task
## State: Closed
## Blocked Reason
## Closed Reason
## Id: 7
## Date Created: 1001
## Date Closed: 1004
## Date Due: 1003
## Pomo Estimate:
## Pomo Completed: 3
## Summary
Task7
## Description
Task7Description
#### Task
## State: Blocked
## Blocked Reason
BlockedReason
## Closed Reason
## Id: 8
## Date Created: 1002
## Date Closed:
## Date Due:
## Pomo Estimate: 10
## Pomo Completed: 4
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
        self.assertIsNone(storage.tasks[0].date_due)
        self.assertIsNone(storage.tasks[0].pomo_estimate)
        self.assertEqual(0, storage.tasks[0].pomo_completed)

        self.assertEqual("Task7", storage.tasks[1].summary)
        self.assertEqual(7, storage.tasks[1].id)
        self.assertEqual("Task7Description", storage.tasks[1].description)
        self.assertTrue(storage.tasks[1].is_closed)
        self.assertEqual(1001, storage.tasks[1].date_created)
        self.assertEqual(1004, storage.tasks[1].date_closed)
        self.assertEqual(1003, storage.tasks[1].date_due)
        self.assertIsNone(storage.tasks[1].pomo_estimate)
        self.assertEqual(3, storage.tasks[1].pomo_completed)

        self.assertEqual("Task8", storage.tasks[2].summary)
        self.assertEqual(8, storage.tasks[2].id)
        self.assertEqual("Task8Description", storage.tasks[2].description)
        self.assertTrue(storage.tasks[2].is_blocked)
        self.assertEqual("BlockedReason", storage.tasks[2].blocked_reason)
        self.assertEqual(1002, storage.tasks[2].date_created)
        self.assertIsNone(storage.tasks[2].date_closed)
        self.assertIsNone(storage.tasks[2].date_due)
        self.assertEqual(10, storage.tasks[2].pomo_estimate)
        self.assertEqual(4, storage.tasks[2].pomo_completed)

    def test_load_invalid_datastore_missing_id(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Blocked Reason
## Closed Reason
## Date Created: 1000
## Date Closed:
## Date Due:
## Pomo Estimate:
## Pomo Completed: 0
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
## Closed Reason
## Id: 4
## Date Created: 1000
## Date Closed:
## Date Due:
## Pomo Estimate:
## Pomo Completed: 0
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
## Closed Reason
## Id: 4
## Date Created: 1000
## Date Closed:
## Date Due:
## Pomo Estimate:
## Pomo Completed: 0
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
## Closed Reason
## Id: 4
## Date Created: 1000
## Date Closed:
## Date Due:
## Pomo Estimate:
## Pomo Completed: 0
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
## Closed Reason
## Id: 4
## Date Created: 1000
## Date Closed:
## Date Due:
## Pomo Estimate:
## Pomo Completed: 0
## Summary
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(TimeDouble())
        self.assertFalse(storage.load('test_file'))

    def test_load_invalid_datastore_missing_closed_reason(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Blocked Reason
## Id: 4
## Date Created: 1000
## Date Closed:
## Date Due:
## Pomo Estimate:
## Pomo Completed: 0
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
## Blocked Reason
## Closed Reason
## Id: 4
## Date Closed:
## Date Due:
## Pomo Estimate:
## Pomo Completed: 0
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
## Blocked Reason
## Closed Reason
## Id: 4
## Date Created: 1000
## Date Due:
## Pomo Estimate:
## Pomo Completed: 0
## Summary
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(TimeDouble())
        self.assertFalse(storage.load('test_file'))

    def test_load_missing_due_date(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Blocked Reason
## Closed Reason
## Id: 4
## Date Created: 1000
## Date Closed:
## Pomo Estimate:
## Pomo Completed: 0
## Summary
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(TimeDouble())
        self.assertFalse(storage.load('test_file'))

    def test_load_missing_pomo_estimate(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Blocked Reason
## Closed Reason
## Id: 4
## Date Created: 1000
## Date Closed:
## Date Due:
## Pomo Completed: 0
## Summary
Task4
## Description
Task4Description
""")
        openDouble.reset()
        openDouble.add_file(fileDouble)

        storage = Storage(TimeDouble())
        self.assertFalse(storage.load('test_file'))

    def test_load_missing_pomo_completed(self):
        fileDouble = FileDouble()
        fileDouble.set_contents("""
#### Task
## State: Open
## Blocked Reason
## Closed Reason
## Id: 4
## Date Created: 1000
## Date Closed:
## Date Due:
## Pomo Estimate:
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
## Closed Reason
## Id: 8
## Date Created: 1000
## Date Closed:
## Date Due:
## Pomo Estimate:
## Pomo Completed: 0
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
        task.close(10003, "Test Reason")
        task.set_due_date(10004.1)
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
## Closed Reason
## Id: 1
## Date Created: 10001
## Date Closed:
## Date Due:
## Pomo Estimate:
## Pomo Completed: 0
## Summary
Task1
## Description
Task1Description word
Multiline
#### Task
## State: Closed
## Blocked Reason
## Closed Reason
Test Reason
## Id: 2
## Date Created: 10002
## Date Closed: 10003
## Date Due: 10004
## Pomo Estimate:
## Pomo Completed: 0
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
## Closed Reason
## Id: 1
## Date Created: 1000
## Date Closed:
## Date Due:
## Pomo Estimate:
## Pomo Completed: 0
## Summary
Task1
## Description
Task1Description word
Multiline
#### Task
## State: Closed
## Blocked Reason
## Closed Reason
## Id: 2
## Date Created: 1001
## Date Closed: 1002
## Date Due:
## Pomo Estimate:
## Pomo Completed: 0
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

class StorageTest_LoadField(unittest.TestCase):
    class TestFile:
        def __init__(self, lines):
            self.lines = lines
            self.index = 0

        def readline(self):
            if self.index == len(self.lines):
                return None
            ret = self.lines[self.index]
            self.index += 1
            return ret

        def close(self):
            None

    def setUp(self):
        None

    def test_LoadField(self):
        s = Storage(TimeDouble())
        tf = self.TestFile([
                "## State: Open",
                "## Blocked Reason",
                "## Closed Reason",
                "## Id: 4",
                "## Date Created: 1000",
                "## Date Closed:",
                "## Date Due:",
                "## Pomo Estimate:",
                "## Pomo Completed: 0",
                "## Summary",
                "Task4",
                "## Description",
                "Task4Description word",
                "multiline",
                "#### Pomo"])
        tf = FileWrapper(tf)

        res, val = s._loadField(tf, "State", hasfield=True, multiline=False)
        self.assertTrue(res)
        self.assertEqual("Open", val)

        res, val = s._loadField(tf, "Blocked Reason", hasfield=True, multiline=True)
        self.assertTrue(res)
        self.assertIsNone(val)

        res, val = s._loadField(tf, "Closed Reason", hasfield=True, multiline=True)
        self.assertTrue(res)
        self.assertIsNone(val)

        res, val = s._loadField(tf, "Id", hasfield=True, multiline=False)
        self.assertTrue(res)
        self.assertEqual('4', val)

        res, val = s._loadField(tf, "Date Created", hasfield=True, multiline=False)
        self.assertTrue(res)
        self.assertEqual("1000", val)

        res, val = s._loadField(tf, "Date Closed", hasfield=True, multiline=False)
        self.assertTrue(res)
        self.assertIsNone(val)

        res, val = s._loadField(tf, "Date Due", hasfield=True, multiline=False)
        self.assertTrue(res)
        self.assertIsNone(val)

        res, val = s._loadField(tf, "Pomo Estimate", hasfield=True, multiline=False)
        self.assertTrue(res)
        self.assertIsNone(val)

        res, val = s._loadField(tf, "Pomo Completed", hasfield=True, multiline=False)
        self.assertTrue(res)
        self.assertEqual("0", val)

        res, val = s._loadField(tf, "Summary", hasfield=True, multiline=True)
        self.assertTrue(res)
        self.assertEqual(["Task4"], val)

        res, val = s._loadField(tf, "Description", hasfield=True, multiline=True)
        self.assertTrue(res)
        self.assertEqual(["Task4Description word","multiline"], val)

        self.assertEqual("#### Pomo", tf.readline())

if __name__ == '__main__':
    unittest.main()
