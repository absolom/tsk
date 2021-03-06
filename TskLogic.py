import os
import unittest
import time
import math
from Task import Task
from Pomo import Pomo

class TaskFactoryDefault:
    def create_task(self, summary, description):
        return Task(summary, description)

class TskLogic:
    def __init__(self, taskFactory=TaskFactoryDefault(), t=time):
        self.tasks = []
        self.taskFactory = taskFactory
        self.time = t

    def set_due_date_relative(self, id, day_offset):
        task = self.get_task(id)
        if not task:
            return False
        seconds_offset = day_offset * 24 * 60 * 60
        task.set_due_date(self.time.time() + seconds_offset)
        return True

    def remove_due_date(self, id):
        task = self.get_task(id)
        if not task:
            return False
        task.remove_due_date()
        return True

    def time_log(self, id, t):
        task = self.get_task(id)
        if task is None:
            return False
        task.log_time(t)
        return True

    def add(self, summary, description=""):
        ntask = self.taskFactory.create_task(summary, description)
        nid = len(self.tasks)+1
        ntask.id = nid
        self.tasks.append(ntask)
        return (True, nid)

    def set_closed(self, id, reason):
        task = self.get_task(id)
        if task is None:
            return False
        task.close(reason=reason)
        return True

    def set_open(self, id):
        task_ids = [x.id for x in self.tasks]
        if not id in task_ids:
            return False
        task = self.get_task(id)
        if not task.open():
            return False
        return True

    def list_tasks(self):
        return self.tasks

    def set_blocked(self, id, reason=""):
        task_ids = [x.id for x in self.tasks]
        if not id in task_ids:
            return False
        index = task_ids.index(id)
        task = self.tasks[index]
        task.block(reason)
        return True

    def get_active(self):
        for task in self.tasks:
            if task.is_active():
                return task.id
        return None

    def set_backlog_position(self, id, pos):
        task = self.get_task(id)
        if task is None:
            return False

        if not task.is_open():
            return False

        open_tasks = [ x for x in self.tasks if x.is_open() ]

        if pos >= len(open_tasks):
            pos = len(open_tasks)

        if pos < 1:
            pos = 0

        index = self.tasks.index(task)
        if pos < len(open_tasks):
            replacing_task = open_tasks[pos]
            self.tasks.remove(task)
            replacing_index = self.tasks.index(replacing_task)
        else:
            replacing_index = len(open_tasks)
            self.tasks.remove(task)
        self.tasks.insert(replacing_index, task)

        return True

    def set_backlog_position_relative(self, id, offset):
        task = self.get_task(id)
        if task is None:
            return False

        if not task.is_open():
            return False

        open_tasks = [ x for x in self.tasks if x.is_open() ]
        pos = open_tasks.index(task)
        newPos = pos + offset
        if newPos > pos:
            newPos += 1

        return self.set_backlog_position(id, newPos)

    def sort_backlog(self, alphaSort=None):
        if alphaSort:
            self.tasks.sort(key = lambda x: x.summary.lower())
        self.tasks.sort(key = lambda x: -x.date_due if x.date_due is not None else None, reverse=True)

    def sort_closed(self):
        self.tasks.sort(key = lambda x: -x.date_closed if x.date_closed is not None else None)

    def set_active(self, id):
        task_ids = [x.id for x in self.tasks]
        if not id in task_ids:
            return False

        if self.get_active():
            index = task_ids.index(self.get_active())
            task = self.tasks[index]
            task.open()

        index = task_ids.index(id)
        task = self.tasks[index]
        task.activate()

        return True

    def get_task(self, id):
        task_ids = [x.id for x in self.tasks]
        if id in task_ids:
            index = task_ids.index(id)
            task = self.tasks[index]
            return task
        return None

    def time_estimate(self, id, estimate):
        task = self.get_task(id)
        if task is None:
            return False
        task.set_estimate(estimate)
        return True

class TskTest(unittest.TestCase):
    class TaskDoubleFactory():
        def __init__(self):
            self.task = None

        def set_task(self, task):
            self.task = task

        def create_task(self, summary, description):
            if self.task is None:
                return Task(summary, description)
            else:
                task = self.task
                self.task = None
                return task

    def setUp(self):
        self.factory = self.TaskDoubleFactory()
        self.tsk = TskLogic(self.factory)

    def test_add_with_description(self):
        self.assertTrue(self.tsk.add("Task1Summary", "Task1Description"))

    def test_add_basic(self):
        self.assertTrue(self.tsk.add("Task1Summary"))

    def test_get_task(self):
        _ , id = self.tsk.add("Task1Summary", "Task1Description")
        task = self.tsk.get_task(id)
        self.assertIsNotNone(task)
        self.assertEquals(Task("Task1Summary", "Task1Description"), task)

    def test_get_task_no_exist(self):
        task = self.tsk.get_task(1)
        self.assertIsNone(task)

    def test_add_default_description(self):
        _ , id = self.tsk.add("Task1Summary")
        self.assertEquals("", self.tsk.get_task(id).description)

    def test_add_duplicate(self):
        self.tsk.add("Task1Summary")
        self.assertTrue(self.tsk.add("Task1Summary")[0])

    def test_add_id(self):
        success, id = self.tsk.add("Task1Summary")
        self.assertIsNotNone(id)

    def test_get_tasks(self):
        self.assertEquals(0, len(self.tsk.list_tasks()))
        self.tsk.add("Task1Summary")
        self.assertEquals(1, len(self.tsk.list_tasks()))
        self.tsk.add("Task2Summary")
        self.assertEquals(2, len(self.tsk.list_tasks()))

    def test_get_active_none(self):
        self.assertIsNone(self.tsk.get_active())

    def test_get_active(self):
        _ , id = self.tsk.add("Task1Summary")
        self.tsk.set_active(id)
        self.assertEquals(id, self.tsk.get_active())

    def test_change_active(self):
        _ , id = self.tsk.add("Task1Summary")
        self.tsk.set_active(id)
        _ , id2 = self.tsk.add("Task2Summary")
        self.tsk.set_active(id2)
        self.assertEquals(id2, self.tsk.get_active())

    def test_list_tasks(self):
        self.tsk.add("Task1Summary")
        tasks = self.tsk.list_tasks()
        self.assertEquals(Task("Task1Summary", ""), tasks[0])

    class TaskDouble:
        def __init__(self, starting_state="Open"):
            self.state = starting_state
            self.open_called = False
            self.open_return = True

        def open(self):
            self.open_called = True
            return self.open_return

class TaskStateTest(unittest.TestCase):

    def setUp(self):
        self.tsk = TskLogic()

    def test_open_closed_task(self):
        _ , id = self.tsk.add("Task1")
        self.tsk.set_closed(id, "Reason")
        self.tsk.set_open(id)
        task = self.tsk.get_task(id)
        self.assertTrue(task.is_open())

    def test_open_open_task(self):
        _ , id = self.tsk.add("Task1")
        self.tsk.set_open(id)
        task = self.tsk.get_task(id)
        self.assertTrue(task.is_open())

    def test_open_active_task(self):
        _ , id = self.tsk.add("Task1")
        self.tsk.set_active(id)
        self.tsk.set_open(id)
        task = self.tsk.get_task(id)
        self.assertTrue(task.is_open())

    def test_only_one_active_task_at_a_time(self):
        _ , id = self.tsk.add("Task1")
        _ , id2 = self.tsk.add("Task2")
        self.tsk.set_active(id)
        self.tsk.set_active(id2)
        task = self.tsk.get_task(id)
        task2 = self.tsk.get_task(id2)
        self.assertFalse(task.is_active())
        self.assertTrue(task2.is_active())

class SortingTest(unittest.TestCase):
    def setUp(self):
        self.tsk = TskLogic()
        _ , self.id1 = self.tsk.add("Task2")
        _ , self.id2 = self.tsk.add("Task1")
        _ , self.id3 = self.tsk.add("Task3")

    def test_sort_closed(self):
        self.tsk.get_task(self.id1).close(3)
        self.tsk.get_task(self.id2).close(1)
        self.tsk.sort_closed()
        tasks = self.tsk.list_tasks()
        self.assertEquals(self.tsk.get_task(self.id3), tasks[0])
        self.assertEquals(self.tsk.get_task(self.id1), tasks[1])
        self.assertEquals(self.tsk.get_task(self.id2), tasks[2])

class TaskIdTest(unittest.TestCase):
    def setUp(self):
        self.tsk = TskLogic()

    def test_task_ids_start_from_1(self):
        _ , id = self.tsk.add("Task")
        self.assertEquals(1, id)

    def test_task_ids_are_sequential(self):
        for i in range(1, 11):
            _ , id = self.tsk.add("Task%d" % i)
            self.assertEquals(id, i)


if __name__ == '__main__':
    unittest.main()

