import unittest
import os
import subprocess
import time
from Storage import Storage
from GoTsk import goTsk
from Task import Task
from TskLogic import TaskFactoryDefault

class PomoDouble:
    def __init__(self):
        pass

    def get_remaining_time(self, t):
        return 0

class TskGitDouble:
    def __init__(self):
        pass

    def commit(self):
        pass

class timeDouble:
    def __init__(self):
        pass

    @staticmethod
    def time():
        return 0

class LockFileDouble:
    @staticmethod
    def exists():
        return False

    @staticmethod
    def create():
        pass

    @staticmethod
    def remove():
        pass

class StorageDouble:
    storages = []
    tasks = []
    def __init__(self, t):
        self.tasks = StorageDouble.tasks
        self.pomo = PomoDouble()

    def load(self, file):
        return True

    def save(self, file):
        return True

    @staticmethod
    def reset():
        StorageDouble.storages = []
        StorageDouble.tasks = []

    @staticmethod
    def add_task(task):
        StorageDouble.tasks.append(task)

    @staticmethod
    def get_task(id):
        for task in StorageDouble.tasks:
            if task.id == id:
                return task
        return None

def openDouble(file, mode):
    pass

class shutilDouble:
    @staticmethod
    def copyfile(f1, f2):
        pass

class PathDouble:
    def __init__(self):
        pass

    def exists(self, path):
        return True

    def isfile(self, file):
        return True

class OsDouble:
    path = PathDouble()

class TskLogicDouble:
    def __init__(self, taskFactory=TaskFactoryDefault(), t=time):
        pass

class TskLogicDoubleFactory:
    @staticmethod
    def get(*args, **kwargs):
        return TskLogicDouble(*args, **kwargs)

class TskFrontEndTest(unittest.TestCase):
    def setUp(self):
        StorageDouble.reset()
        task = Task("Task4", "", 0)
        task.id = 4
        StorageDouble.add_task(task)

    def tearDown(self):
        pass

    def _runTsk(self, args):
        return goTsk(arguments=args.split(" "),
            LockFileCls=LockFileDouble,
            git=TskGitDouble(),
            shutil=shutilDouble,
            open=openDouble,
            os=OsDouble,
            StorageCls=StorageDouble,
            time=timeDouble)

    def test_set_due_date_relative(self):

        self.assertTrue(self._runTsk('set_due_date 4 +10'))
        self.assertEquals(StorageDouble.get_task(4).date_due, 10*24*60*60)
        self.assertFalse(self._runTsk('set_due_date 2 +10'))
        self.assertFalse(self._runTsk('set_due_date 4 10'))
        self.assertEquals(StorageDouble.get_task(4).date_due, 10*24*60*60)

    def test_remove_due_date(self):

        self._runTsk('set_due_date 4 +10')
        self.assertTrue(self._runTsk('remove_due_date 4'))
        self.assertEquals(StorageDouble.get_task(4).date_due, None)

        self.assertFalse(self._runTsk('remove_due_date 5'))

    def test_time_log(self):

        self.assertTrue(self._runTsk('time_log 4 60'))
        self.assertEquals(StorageDouble.get_task(4).time_spent, 60)

        self.assertFalse(self._runTsk('time_log 5 60'))

    def test_sort_backlog(self):
        StorageDouble.reset()
        #            [Summary, id, due_date]
        tasksTruth = [["Task1", 1, 9],
                      ["Task2", 2, 8],
                      ["Task3", 3, 7],
                      ["Task4", 4, 6],
                      ["Taske", 5, 5],
                      ["Taskd", 6, 4],
                      ["Taskc", 7, 3],
                      ["Taskb", 8, 2],
                      ["Taska", 9, 1]]
        # Add some tasks and set due dates
        for truth in tasksTruth:
            task = Task(truth[0], "", 0)
            task.id = truth[1]
            task.set_due_date(truth[2])
            StorageDouble.add_task(task)

        # Verify they get sorted correctly
        self.assertTrue(self._runTsk('sort_backlog'))
        idOrderTruth = [9, 8, 7, 6, 5, 4, 3, 2, 1]
        idOrder = [ t.id for t in StorageDouble.tasks ]
        self.assertEquals(idOrderTruth, idOrder)

    def test_sort_backlog_alphanumeric(self):
        StorageDouble.reset()
        #            [Summary, id, due_date]
        tasksTruth = [["Task1", 1, 9],
                      ["Task2", 2, 8],
                      ["Task3", 3, 7],
                      ["Task4", 4, 6],
                      ["Taske", 5, None],
                      ["Taskd", 6, None],
                      ["Taskc", 7, None],
                      ["Taskb", 8, None],
                      ["Taska", 9, None]]

        # Add some tasks and set due dates
        for truth in tasksTruth:
            task = Task(truth[0], "", 0)
            task.id = truth[1]
            task.set_due_date(truth[2])
            StorageDouble.add_task(task)

        # Verify they get sorted correctly
        self.assertTrue(self._runTsk('sort_backlog -a'))
        idOrderTruth = [4, 3, 2, 1, 9, 8, 7, 6, 5]
        idOrder = [ t.id for t in StorageDouble.tasks ]
        self.assertEquals(idOrderTruth, idOrder)

    def test_time_estimate(self):
        self.assertTrue(self._runTsk('time_estimate 4 60'))
        self.assertEquals(StorageDouble.get_task(4).time_estimate, 60)

        self.assertFalse(self._runTsk('time_estimate 5 60'))

    def test_close(self):
        task = Task("Task", "", 0)
        task.id = 1
        task.open()
        StorageDouble.add_task(task)

        self.assertTrue(self._runTsk('close 1'))
        self.assertTrue(StorageDouble.get_task(1).is_closed())

        self.assertFalse(self._runTsk('close 2'))

    def test_close_reason(self):
        task = Task("Task", "", 0)
        task.id = 1
        task.open()
        StorageDouble.add_task(task)

        self.assertTrue(self._runTsk('close 1 --r=Reason'))
        self.assertTrue(StorageDouble.get_task(1).is_closed())
        self.assertEquals("Reason", StorageDouble.get_task(1).closed_reason)

        self.assertFalse(self._runTsk('close 2'))

    def test_open(self):
        task = Task("Task", "", 0)
        task.id = 1
        task.close()
        StorageDouble.add_task(task)

        self.assertTrue(self._runTsk('open 1'))
        self.assertTrue(StorageDouble.get_task(1).is_open())

        self.assertFalse(self._runTsk('open 2'))

    def test_block(self):
        self.assertTrue(self._runTsk('block 4 Reason'))
        self.assertEquals("Reason", StorageDouble.get_task(4).blocked_reason)
        self.assertTrue(self._runTsk('block 4 Reason2'))
        self.assertEquals("Reason2", StorageDouble.get_task(4).blocked_reason)

        self.assertFalse(self._runTsk('block 1 Reason'))

if __name__ == '__main__':
    unittest.main()
