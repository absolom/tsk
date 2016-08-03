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
        # task = Task("Task4", "", 0)
        # task.id = 4
        # self.tasks = [task]
        # self.pomo = PomoDouble()
        # StorageDouble.storages.append(self)

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
        StorageDouble.tasks = []
        # Add some tasks and set due dates
        for i in range(1, 10):
            task = Task("Task{:d}".format(i), "", 0)
            task.id = i
            task.set_due_date((10 - i))
            StorageDouble.add_task(task)

        # Verify they get sorted correctly
        self.assertTrue(self._runTsk('sort_backlog'))
        for i in range(1, 10):
            self.assertEquals(i, StorageDouble.tasks[-i].id)

    def test_sort_backlog_alphanumeric(self):
        StorageDouble.tasks = []
        # Add some tasks and set due dates
        for i in range(1, 5):
            task = Task("Task{:d}".format(i), "", 0)
            task.id = i
            task.set_due_date((10 - i))
            StorageDouble.add_task(task)

        for i in range(5, 10):
            task = Task("Task{:s}".format(chr(45-i)), "", 0)
            task.id = i
            StorageDouble.add_task(task)

        # Verify they get sorted correctly
        self.assertTrue(self._runTsk('sort_backlog -a'))
        for i in range(1, 5):
            self.assertEquals(i, StorageDouble.tasks[-(i+5)].id)
        for i in range(5, 10):
            self.assertEquals(i, StorageDouble.tasks[-(i-4)].id)

if __name__ == '__main__':
    unittest.main()
