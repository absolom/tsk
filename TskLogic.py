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
    def __init__(self, taskFactory=TaskFactoryDefault()):
        self.tasks = []
        self.taskFactory = taskFactory

    def add(self, summary, description=""):
        ntask = self.taskFactory.create_task(summary, description)
        nid = len(self.tasks)+1
        ntask.id = nid
        self.tasks.append(ntask)
        return (True, nid)

    def set_closed(self, id):
        task = self.get_task(id)
        if task is None:
            return False
        if task.is_closed():
            return False
        task.close()
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
        if pos > len(self.tasks):
            return False

        task_ids = [x.id for x in self.tasks]
        if not id in task_ids:
            return False

        index = task_ids.index(id)
        task = self.tasks[index]
        self.tasks.remove(task)
        self.tasks.insert(pos, task)

        return True

    def sort_backlog(self):
        self.tasks.sort(key = lambda x: -x.date_due if x.date_due is not None else None, reverse=True)

    def sort_closed(self):
        self.tasks.sort(key = lambda x: -x.date_closed if x.date_closed is not None else None)

    def set_backlog_position_relative(self, id, offset):
        # Verify the task exists
        task_ids = [x.id for x in self.tasks]
        if not id in task_ids:
            return False

        # Get position and Task instance
        pos = task_ids.index(id)
        task = self.tasks[pos]

        # Verify it is in the backlog
        if not task.is_open():
            return False

        # check current position+offset for out of bounds
        newPos = pos + offset

        if newPos > len(self.tasks):
            newPos = len(self.tasks)
        if newPos < 0:
            newPos = 0

        # move to new position
        return self.set_backlog_position(id, newPos)

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

    def test_set_active(self):
        _ , id = self.tsk.add("Task1Summary")
        self.assertTrue(self.tsk.set_active(id))

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

    def test_set_active_nonexist(self):
        self.assertFalse(self.tsk.set_active(0))

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

    def test_open(self):
        dbl = self.TaskDouble()
        self.factory.set_task(dbl)
        _ , id = self.tsk.add("Summary")
        self.assertTrue(self.tsk.set_open(id))
        self.assertTrue(dbl.open_called)

    def test_open_badid(self):
        self.assertFalse(self.tsk.set_open(10))

    def test_open_badstate(self):
        dbl = self.TaskDouble()
        dbl.open_return = False
        self.factory.set_task(dbl)
        _ , id = self.tsk.add("Summary")
        self.assertFalse(self.tsk.set_open(id))

class TaskStateTest(unittest.TestCase):

    def setUp(self):
        self.tsk = TskLogic()

    def test_open_closed_task(self):
        _ , id = self.tsk.add("Task1")
        self.tsk.set_closed(id)
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

    def test_close_open_task(self):
        _ , id = self.tsk.add("Task1")
        self.assertTrue(self.tsk.set_closed(id))
        task = self.tsk.get_task(id)
        self.assertTrue(task.is_closed())

    def test_close_invalid_id(self):
        self.assertFalse(self.tsk.set_closed(1))

    def test_close_closed_task(self):
        _ , id = self.tsk.add("Task1")
        self.assertTrue(self.tsk.set_closed(id))
        self.assertFalse(self.tsk.set_closed(id))

    def test_close_active_task(self):
        _ , id = self.tsk.add("Task1")
        self.tsk.set_active(id)
        self.assertTrue(self.tsk.set_closed(id))

    def test_set_active_flags_task_as_active(self):
        _ , id = self.tsk.add("Task1")
        self.tsk.set_active(id)
        task = self.tsk.get_task(id)
        self.assertTrue(task.is_active())

    def test_only_one_active_task_at_a_time(self):
        _ , id = self.tsk.add("Task1")
        _ , id2 = self.tsk.add("Task2")
        self.tsk.set_active(id)
        self.tsk.set_active(id2)
        task = self.tsk.get_task(id)
        task2 = self.tsk.get_task(id2)
        self.assertFalse(task.is_active())
        self.assertTrue(task2.is_active())

    def test_set_blocked(self):
        _ , id = self.tsk.add("Task1")
        self.assertTrue(self.tsk.set_blocked(id, "BlockedReason"))
        task = self.tsk.get_task(id)
        self.assertTrue(task.is_blocked())

    def test_set_blocked_invalid_id(self):
        self.assertFalse(self.tsk.set_blocked(1, "BlockedReason"))

    def test_get_blocked_reason(self):
        _ , id = self.tsk.add("Task1")
        self.tsk.set_blocked(id, "BlockedReason")
        task = self.tsk.get_task(id)
        self.assertEquals("BlockedReason", task.blocked_reason)

    def test_get_blocked_reason_default(self):
        _ , id = self.tsk.add("Task1")
        self.tsk.set_blocked(id)
        task = self.tsk.get_task(id)
        self.assertEquals("", task.blocked_reason)

class SortingTest(unittest.TestCase):
    def setUp(self):
        self.tsk = TskLogic()
        _ , self.id1 = self.tsk.add("Task1")
        _ , self.id2 = self.tsk.add("Task2")
        _ , self.id3 = self.tsk.add("Task3")

    def test_sort_backlog(self):
        self.tsk.get_task(self.id1).set_due_date(1000)
        self.tsk.get_task(self.id3).set_due_date(999)
        self.tsk.sort_backlog()
        tasks = self.tsk.list_tasks()
        self.assertEquals(self.tsk.get_task(self.id3), tasks[0])
        self.assertEquals(self.tsk.get_task(self.id1), tasks[1])
        self.assertEquals(self.tsk.get_task(self.id2), tasks[2])

    def test_sort_closed(self):
        self.tsk.get_task(self.id1).close(3)
        self.tsk.get_task(self.id2).close(1)
        self.tsk.sort_closed()
        tasks = self.tsk.list_tasks()
        self.assertEquals(self.tsk.get_task(self.id3), tasks[0])
        self.assertEquals(self.tsk.get_task(self.id1), tasks[1])
        self.assertEquals(self.tsk.get_task(self.id2), tasks[2])

class TaskBacklogTest(unittest.TestCase):
    def setUp(self):
        self.tsk = TskLogic()
        _ , self.id1 = self.tsk.add("Task1")
        _ , self.id2 = self.tsk.add("Task2")
        _ , self.id3 = self.tsk.add("Task3")

    def test_backlog_default_order(self):
        tasks = self.tsk.list_tasks()
        self.assertEquals(self.tsk.get_task(self.id1), tasks[0])
        self.assertEquals(self.tsk.get_task(self.id2), tasks[1])
        self.assertEquals(self.tsk.get_task(self.id3), tasks[2])

    def test_backlog_set_pos(self):
        self.assertTrue(self.tsk.set_backlog_position(self.id2, 0))
        tasks = self.tsk.list_tasks()
        self.assertEquals(self.tsk.get_task(self.id2), tasks[0])
        self.assertEquals(self.tsk.get_task(self.id1), tasks[1])
        self.assertEquals(self.tsk.get_task(self.id3), tasks[2])

    def test_backlog_set_pos_invalid_pos(self):
        self.assertFalse(self.tsk.set_backlog_position(self.id2, 5))

    def test_backlog_set_pos_invalid_id(self):
        self.assertFalse(self.tsk.set_backlog_position(10, 1))

    def test_backlog_set_pos_bottom(self):
        self.assertTrue(self.tsk.set_backlog_position(self.id2, 3))
        tasks = self.tsk.list_tasks()
        self.assertEquals(self.tsk.get_task(self.id1), tasks[0])
        self.assertEquals(self.tsk.get_task(self.id3), tasks[1])
        self.assertEquals(self.tsk.get_task(self.id2), tasks[2])

    def test_backlog_set_pos_rel_positive(self):
        self.assertTrue(self.tsk.set_backlog_position_relative(self.id2, 1))
        tasks = self.tsk.list_tasks()
        self.assertEquals(self.tsk.get_task(self.id1), tasks[0])
        self.assertEquals(self.tsk.get_task(self.id3), tasks[1])
        self.assertEquals(self.tsk.get_task(self.id2), tasks[2])

    def test_backlog_set_pos_rel_negative(self):
        self.assertTrue(self.tsk.set_backlog_position_relative(self.id2, -1))
        tasks = self.tsk.list_tasks()
        self.assertEquals(self.tsk.get_task(self.id2), tasks[0])
        self.assertEquals(self.tsk.get_task(self.id1), tasks[1])
        self.assertEquals(self.tsk.get_task(self.id3), tasks[2])

    def test_backlog_set_pos_rel_oob_negative(self):
        self.assertTrue(self.tsk.set_backlog_position_relative(self.id2, -100))
        tasks = self.tsk.list_tasks()
        self.assertEquals(self.tsk.get_task(self.id2), tasks[0])
        self.assertEquals(self.tsk.get_task(self.id1), tasks[1])
        self.assertEquals(self.tsk.get_task(self.id3), tasks[2])

    def test_backlog_set_pos_rel_oob_positive(self):
        self.assertTrue(self.tsk.set_backlog_position_relative(self.id2, 100))
        tasks = self.tsk.list_tasks()
        self.assertEquals(self.tsk.get_task(self.id1), tasks[0])
        self.assertEquals(self.tsk.get_task(self.id3), tasks[1])
        self.assertEquals(self.tsk.get_task(self.id2), tasks[2])

    def test_backlog_set_pos_rel_not_in_backlog(self):
        self.tsk.get_task(self.id1).close()
        self.assertFalse(self.tsk.set_backlog_position_relative(self.id1, 1))

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

