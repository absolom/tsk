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
    def __init__(self, t):
        task = Task("Task4", "", 0)
        task.id = 4
        self.tasks = [task]
        self.pomo = PomoDouble()
        StorageDouble.storages.append(self)

    def load(self, file):
        return True

    def save(self, file):
        return True

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
        pass

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
        self.assertEquals(StorageDouble.storages[-1].tasks[0].date_due, 10*24*60*60)

        self.assertFalse(self._runTsk('set_due_date 2 +10'))
        self.assertEquals(StorageDouble.storages[-1].tasks[0].date_due, None)

        self.assertFalse(self._runTsk('set_due_date 4 10'))
        self.assertEquals(StorageDouble.storages[-1].tasks[0].date_due, None)

    def test_remove_due_date(self):

        self._runTsk('set_due_date 4 +10')
        self.assertTrue(self._runTsk('remove_due_date 4'))
        self.assertEquals(StorageDouble.storages[-1].tasks[0].date_due, None)

        self.assertFalse(self._runTsk('remove_due_date 5'))

    def test_time_log(self):

        self.assertTrue(self._runTsk('time_log 4 60'))
        self.assertEquals(StorageDouble.storages[-1].tasks[0].time_spent, 60)

        self.assertFalse(self._runTsk('time_log 5 60'))

if __name__ == '__main__':
    unittest.main()
