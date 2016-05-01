import os
import unittest

class Task:
    def __init__(self, summary, description):
        self.summary = summary
        self.description = description
        self.blocked_reason = None
        self.id = None
        self.state = "Open"

    def __eq__(self, other):
        return self.summary == other.summary and self.description == other.description

    def is_active(self):
        return self.state == "Active"

    def is_blocked(self):
        return self.state == "Blocked"

    def is_closed(self):
        return self.state == "Closed"

    def is_open(self):
        return self.state == "Open"

    def close(self):
        self.state = "Closed"

    def open(self):
        self.state = "Open"

    def block(self, reason):
        self.state = "Blocked"
        self.blocked_reason = reason

    def activate(self):
        self.state = "Active"

class TskFrontEnd:
    def __init__(self, tsk):
        self.tsk = tsk

    def get_active_string(self):
        if self.tsk.get_active() == None:
            return "No Active Task."

        active_task = self.tsk.get_task(self.tsk.get_active())
        return "{:s}\n{:<3x}   {:s}".format("Active Task", self.tsk.get_active(), active_task.summary)

    def get_backlog_string(self):
        ret = "Backlog\n"
        output = 0
        for i, task in enumerate(self.tsk.list_tasks()):
            if task.is_active():
                continue
            ret += "{:<3x}   {:s}\n".format(task.id, task.summary)
            output += 1
            if output > 3:
                ret += "... {:d} More".format(len(self.tsk.list_tasks()) - i)
                break

        return ret

class Tsk:
    def __init__(self):
        self.tasks = []
        self.active_id = None


    def add(self, summary, description=""):
        ntask = Task(summary, description)
        if ntask in self.tasks:
            return False
        nid = len(self.tasks)+1
        ntask.id = nid
        self.tasks.append(ntask)
        return (True, nid)

    def set_closed(self, id):
        task = self.get_task(id)
        task.close()

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
        return self.active_id

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

    def set_active(self, id):
        task_ids = [x.id for x in self.tasks]
        if not id in task_ids:
            return False

        if self.active_id:
            index = task_ids.index(self.active_id)
            task = self.tasks[index]
            task.open()

        index = task_ids.index(id)
        task = self.tasks[index]
        task.activate()
        self.active_id = id

        return True

    def get_task(self, id):
        task_ids = [x.id for x in self.tasks]
        index = task_ids.index(id)
        task = self.tasks[index]
        return task

class TaskTest(unittest.TestCase):
    def setUp(self):
        self.task = Task("Task1", "")

    def test_default_is_open(self):
        self.assertTrue(self.task.is_open())

    def test_open_to_closed(self):
        self.task.close()
        self.assertTrue(self.task.is_closed())
        self.assertFalse(self.task.is_open())

    def test_open_to_blocked(self):
        self.task.block("Reason")
        self.assertFalse(self.task.is_open())
        self.assertTrue(self.task.is_blocked())
        self.assertEquals("Reason", self.task.blocked_reason)

    def test_open_to_active(self):
        self.task.activate()
        self.assertFalse(self.task.is_open())
        self.assertTrue(self.task.is_active())

    def test_closed_to_open(self):
        self.task.close()
        self.assertFalse(self.task.is_open())
        self.assertTrue(self.task.is_closed())

    def test_blocked_to_open(self):
        self.task.block("Reason")
        self.task.open()
        self.assertFalse(self.task.is_blocked())
        self.assertTrue(self.task.is_open())

    def test_blocked_to_closed(self):
        self.task.block("Reason")
        self.task.close()
        self.assertFalse(self.task.is_blocked())
        self.assertTrue(self.task.is_closed())

    def test_blocked_to_active(self):
        self.task.block("Reason")
        self.task.activate()
        self.assertFalse(self.task.is_blocked())
        self.assertTrue(self.task.is_active())

    def test_active_to_closed(self):
        self.task.activate()
        self.task.close()
        self.assertFalse(self.task.is_active())
        self.assertTrue(self.task.is_closed())

    def test_active_to_open(self):
        self.task.activate()
        self.task.open()
        self.assertFalse(self.task.is_active())
        self.assertTrue(self.task.is_open())

    def test_active_to_blocked(self):
        self.task.activate()
        self.task.block("Reason")
        self.assertFalse(self.task.is_active())
        self.assertTrue(self.task.is_blocked())

    def test_set_blocked_reason(self):
        self.task.block("Reason")
        self.assertEquals("Reason", self.task.blocked_reason)

class TskTest(unittest.TestCase):

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

    def test_open_closed_task(self):
        None

    def test_open_open_task(self):
        None

    def test_open_active_task(self):
        None

    def test_close_open_task(self):
        _ , id = self.tsk.add("Task1")
        self.tsk.set_closed(id)
        task = self.tsk.get_task(id)
        self.assertTrue(task.is_closed())

    def test_close_closed_task(self):
        None

    def test_close_active_task(self):
        None

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
        self.tsk.add("Task1")
        self.tsk.add("Task2", "Task2 Description")
        self.tsk.add("Task3")
        self.tsk.add("Task4", "Task4 Description")

        for i in range(5, 15):
            self.tsk.add("Task%d" % i)

        self.tskfe = TskFrontEnd(self.tsk)

    def test_get_active_string_no_active(self):
        status_active_truth = """No Active Task."""
        self.assertEquals(status_active_truth, self.tskfe.get_active_string())

    def test_get_active_string_with_active(self):
        self.tsk.set_active(1)
        status_active_truth = """Active Task
1     Task1"""
        self.assertEquals(status_active_truth, self.tskfe.get_active_string())

    def test_get_backlog(self):
        backlog_truth = """Backlog
1     Task1
2     Task2
3     Task3
4     Task4
... 11 More"""
        self.assertEquals(backlog_truth, self.tskfe.get_backlog_string())

    def test_get_backlog_with_active(self):
        self.tsk.set_active(3)
        backlog_truth = """Backlog
1     Task1
2     Task2
4     Task4
5     Task5
... 10 More"""
        self.assertEquals(backlog_truth, self.tskfe.get_backlog_string())

    def test_get_backlog_none(self):
        self.tskfe = TskFrontEnd(Tsk())
        self.assertEquals("Backlog\n", self.tskfe.get_backlog_string())

if __name__ == '__main__':
    unittest.main()


