import os
import unittest

class Task:
    def __init__(self, summary, description):
        self.summary = summary
        self.description = description
        self.active = False
        self.blocked = False
        self.blocked_reason = None

    def __eq__(self, other):
        return self.summary == other.summary and self.description == other.description

    def is_active(self):
        return self.active

    def is_blocked(self):
        return self.blocked

class Tsk:
    def __init__(self):
        self.tasks = []
        self.active_id = None
        self.task_ids = []

    def add(self, summary, description=""):
        ntask = Task(summary, description)
        if ntask in self.tasks:
            return False
        nid = len(self.tasks)+1
        self.task_ids.append(nid)
        self.tasks.append(ntask)
        return (True, nid)

    def list_tasks(self):
        return self.tasks

    def set_blocked(self, id, reason=""):
        if not id in self.task_ids:
            return False
        index = self.task_ids.index(id)
        task = self.tasks[index]
        task.blocked = True
        task.blocked_reason = reason
        return True

    def get_active(self):
        return self.active_id

    def set_backlog_position(self, id, pos):
        if pos > len(self.task_ids):
            return False

        if not id in self.task_ids:
            return False

        index = self.task_ids.index(id)
        self.task_ids.remove(id)
        self.task_ids.insert(pos, id)

        task = self.tasks[index]
        self.tasks.remove(task)
        self.tasks.insert(pos, task)

        return True

    def set_active(self, id):
        if not id in self.task_ids:
            return False

        if self.active_id:
            index = self.task_ids.index(self.active_id)
            task = self.tasks[index]
            task.active = False

        index = self.task_ids.index(id)
        task = self.tasks[index]
        task.active = True
        self.active_id = id

        return True

    def get_task(self, id):
        index = self.task_ids.index(id)
        task = self.tasks[index]
        return task

class TaskTest(unittest.TestCase):

    def setUp(self):
        self.tsk = Tsk()

    def test_add_with_description(self):
        self.assertTrue(self.tsk.add("Task1Summary", "Task1Description"))

    def test_add_basic(self):
        self.assertTrue(self.tsk.add("Task1Summary"))

    def test_get_task(self):
        _ , id = self.tsk.add("Task1Summary", "Task1Description")
        task = self.tsk.get_task(id)
        self.assertIsNotNone(task)
        self.assertEquals(Task("Task1Summary", "Task1Description"), task)

    def test_add_default_description(self):
        _ , id = self.tsk.add("Task1Summary")
        self.assertEquals("", self.tsk.get_task(id).description)

    def test_add_duplicate(self):
        self.tsk.add("Task1Summary")
        self.assertFalse(self.tsk.add("Task1Summary"))

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

class TaskStateTest(unittest.TestCase):

    def setUp(self):
        self.tsk = Tsk()

    def test_open_task(self):
        None

    def test_close_task(self):
        None

    def test_close_active_task(self):
        None

    def test_active_state(self):
        _ , id = self.tsk.add("Task1")
        self.tsk.set_active(id)
        task = self.tsk.get_task(id)
        self.assertTrue(task.is_active())

    def test_only_one_active(self):
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

class TaskBacklogTest(unittest.TestCase):
    def setUp(self):
        self.tsk = Tsk()
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

class TaskIdTest(unittest.TestCase):
    def setUp(self):
        self.tsk = Tsk()

    def test_task_ids_start_from_1(self):
        _ , id = self.tsk.add("Task")
        self.assertEquals(1, id)

    def test_task_ids_are_sequential(self):
        for i in range(1, 11):
            _ , id = self.tsk.add("Task%d" % i)
            self.assertEquals(id, i)

class StringsTest(unittest.TestCase):
    def setUp(self):
        self.tsk = Tsk()

    def test_verify_status_string(self):
        None

    def test_backlog_string(self):
        None

if __name__ == '__main__':
    unittest.main()


