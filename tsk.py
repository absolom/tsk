import os
import unittest
import time
import math

class TskFrontEnd:
    def __init__(self, tsk=None, renderTsk=None, renderPomo=None):
        self.tsk = tsk
        self.renderTsk = renderTsk
        self.renderPomo = renderPomo

    def add_task(self, summary, description):
        ret , id = self.tsk.add(summary, description)
        return "Task {:d} added.".format(id)

    def status(self):
        ret = self.renderPomo.get_status_string(0)
        ret += self.renderTsk.get_active_string()
        ret += self.renderTsk.get_blocked_summary_string()
        ret += self.renderTsk.get_backlog_summary_string()
        return ret

    def backlog(self):
        ret = self.renderTsk.get_backlog_summary_string()
        return ret

    def block(self, id, reason):
        if self.tsk.set_blocked(id, reason):
            return "Task {:d} marked blocked.".format(id)
        else:
            return "Failed to mark task {:d} blocked.".format(id)


class PomoRender:
    def __init__(self, pomo):
        self.pomo = pomo

    def get_status_string(self, t):
        remaining = self.pomo.get_remaining_time(t)
        minutes = int(math.floor(remaining / 60))
        seconds = int(math.floor(remaining - 60*minutes))
        if minutes == 0 and seconds == 0:
            return "Pomodoro: 0:00 COMPLETE".format(minutes, seconds)

        if self.pomo.is_paused():
            return "Pomodoro: {:d}:{:02d} PAUSED".format(minutes, seconds)

        return "Pomodoro: {:d}:{:02d}".format(minutes, seconds)

class Pomo:
    def __init__(self):
        self.start_time = None
        self.running = False
        self.elapsed = 0.0

    def start(self, t):
        if not self.running:
            self.start_time = t
            self.running = True

    def get_remaining_time(self, t):
        elapsed_this_lap = 0
        if self.running:
            elapsed_this_lap = t - self.start_time
        remaining_time = 25*60 - round(self.elapsed + elapsed_this_lap)
        if remaining_time < 0:
            remaining_time = 0
        return remaining_time

    def pause(self, t):
        if self.running:
            self.elapsed += t - self.start_time
            self.running = False

    def is_paused(self):
        return not self.running

    def is_expired(self, t):
        return self.get_remaining_time(t) <= 0

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

class TskTextRender:
    def __init__(self, tsk):
        self.tsk = tsk

    def get_active_string(self):
        if self.tsk.get_active() == None:
            return "No Active Task."

        active_task = self.tsk.get_task(self.tsk.get_active())
        return "{:s}\n{:<3x}   {:s}".format("Active Task", self.tsk.get_active(), active_task.summary)

    def get_backlog_summary_string(self):
        ret = "Backlog"
        output = 0
        for i, task in enumerate(self.tsk.list_tasks()):
            if task.is_active():
                continue
            if task.is_closed():
                continue
            if task.is_blocked():
                continue
            ret += "\n{:<3x}   {:s}".format(task.id, task.summary)
            output += 1
            if output > 3:
                ret += "\n... {:d} More".format(len(self.tsk.list_tasks()) - i)
                break

        return ret

    def get_blocked_summary_string(self):
        ret = "Blocked"
        output = 0
        for i, task in enumerate(self.tsk.list_tasks()):
            if not task.is_blocked():
                continue

            ret += "\n{:<3x}   {:s}   {:s}".format(task.id, task.summary, task.blocked_reason)
            output += 1
            if output > 3:
                ret += "\n... {:d} More".format(len(self.tsk.list_tasks()) - i)
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

        self.tskfe = TskTextRender(self.tsk)

    def test_get_active_string_no_active(self):
        status_active_truth = """No Active Task."""
        self.assertEquals(status_active_truth, self.tskfe.get_active_string())

    def test_get_active_string_with_active(self):
        self.tsk.set_active(1)
        status_active_truth = """Active Task
1     Task1"""
        self.assertEquals(status_active_truth, self.tskfe.get_active_string())

    def test_get_backlog_summary(self):
        self.tsk = Tsk()
        self.tsk.add("Task1")
        self.tsk.add("Task2", "Task2 Description")
        self.tskfe = TskTextRender(self.tsk)
        backlog_truth = """Backlog
1     Task1
2     Task2"""
        self.assertEquals(backlog_truth, self.tskfe.get_backlog_summary_string())

    def test_get_backlog_summary_overflow(self):
        backlog_truth = """Backlog
1     Task1
2     Task2
3     Task3
4     Task4
... 11 More"""
        self.assertEquals(backlog_truth, self.tskfe.get_backlog_summary_string())

    def test_get_backlog_summary_with_active(self):
        self.tsk.set_active(3)
        backlog_truth = """Backlog
1     Task1
2     Task2
4     Task4
5     Task5
... 10 More"""
        self.assertEquals(backlog_truth, self.tskfe.get_backlog_summary_string())

    def test_get_backlog_summary_none(self):
        self.tskfe = TskTextRender(Tsk())
        self.assertEquals("Backlog", self.tskfe.get_backlog_summary_string())

    def test_get_backlog_summary_skips_closed(self):
        self.tsk.set_closed(3)
        self.tsk.set_closed(5)
        backlog_truth = """Backlog
1     Task1
2     Task2
4     Task4
6     Task6
... 9 More"""
        self.assertEquals(backlog_truth, self.tskfe.get_backlog_summary_string())

    def test_get_backlog_summary_skips_blocked(self):
        self.tsk.set_blocked(3, "Reason")
        self.tsk.set_blocked(5, "Reason")
        backlog_truth = """Backlog
1     Task1
2     Task2
4     Task4
6     Task6
... 9 More"""
        self.assertEquals(backlog_truth, self.tskfe.get_backlog_summary_string())

    def test_get_blocked_status(self):
        self.tsk.set_blocked(3, "Reason1")
        self.tsk.set_blocked(5, "Reason2")
        blocked_truth = """Blocked
3     Task3   Reason1
5     Task5   Reason2"""
        self.assertEquals(blocked_truth, self.tskfe.get_blocked_summary_string())

    def test_get_blocked_status_empty(self):
        blocked_truth = """Blocked"""
        self.assertEquals(blocked_truth, self.tskfe.get_blocked_summary_string())

    def test_get_blocked_status_overflow(self):
        for i in range(1,15):
            self.tsk.set_blocked(i, "Reason{:d}".format(i))
        blocked_truth = """Blocked
1     Task1   Reason1
2     Task2   Reason2
3     Task3   Reason3
4     Task4   Reason4
... 11 More"""
        self.assertEquals(blocked_truth, self.tskfe.get_blocked_summary_string())

class PomoStringsTest(unittest.TestCase):
    def setUp(self):
        self.pomo = Pomo()
        self.rndr = PomoRender(self.pomo)

    def test_get_status_default(self):
        truth = """Pomodoro: 25:00 PAUSED"""
        self.assertEquals(truth, self.rndr.get_status_string(0))

    def test_get_status_running(self):
        self.pomo.start(0)
        truth = """Pomodoro: 24:55"""
        self.assertEquals(truth, self.rndr.get_status_string(5))

    def test_get_status_paused(self):
        self.pomo.start(0)
        self.pomo.pause(1)
        truth = """Pomodoro: 24:59 PAUSED"""
        self.assertEquals(truth, self.rndr.get_status_string(5))

    def test_get_status_running(self):
        self.pomo.start(0)
        truth = """Pomodoro: 0:00 COMPLETE"""
        self.assertEquals(truth, self.rndr.get_status_string(60*25))

class PomoTest(unittest.TestCase):
    def setUp(self):
        self.pomo = Pomo()

    def test_remaining_time_default(self):
        self.assertEquals(25*60, self.pomo.get_remaining_time(time.time()))

    def test_remaining_time_decreases_correctly(self):
        self.pomo.start(0.0)
        self.assertEquals(25*60 - 3, self.pomo.get_remaining_time(3.0))

    def test_remaining_time_rounds_up(self):
        self.pomo.start(0.0)
        self.assertEquals(25*60 - 3, self.pomo.get_remaining_time(2.5))

    def test_remaining_time_rounds_down(self):
        self.pomo.start(0.0)
        self.assertEquals(25*60 - 3, self.pomo.get_remaining_time(3.49))

    def test_remaining_time_finished(self):
        self.pomo.start(0)
        self.assertEquals(0, self.pomo.get_remaining_time(25*60*2))

    def test_paused_remaining_time(self):
        self.pomo.start(0.0)
        self.pomo.pause(3.0)
        self.assertEquals(25*60 - 3, self.pomo.get_remaining_time(100.0))

    def test_pause_start(self):
        self.pomo.start(0.0)
        self.pomo.pause(3.0)
        self.pomo.start(6.0)
        self.assertEquals(25*60 - 6, self.pomo.get_remaining_time(9.0))

    def test_double_pause(self):
        self.pomo.start(0.0)
        self.pomo.pause(3.0)
        self.pomo.pause(6.0)
        self.assertEquals(25*60 - 3, self.pomo.get_remaining_time(9.0))

    def test_double_start(self):
        self.pomo.start(0.0)
        self.pomo.start(3.0)
        self.assertEquals(25*60 - 6, self.pomo.get_remaining_time(6.0))

    def test_expired_default(self):
        self.assertFalse(self.pomo.is_expired(100))

    def test_expired_positive(self):
        self.pomo.start(0.0)
        self.assertTrue(self.pomo.is_expired(25*60+1))

    def test_expired_negative(self):
        self.pomo.start(0.0)
        self.assertFalse(self.pomo.is_expired(25*60-1))

class PomoRenderDouble:
    def __init__(self):
        self.get_status_string_called = False
        self.get_status_string_response = ""

    def set_get_status_string_response(self, resp):
        self.get_status_string_response = resp

    def get_status_string(self, t):
        self.get_status_string_called = True
        return self.get_status_string_response

class TskTextRenderDouble:
    def __init__(self):
        self.get_active_string_called = False
        self.get_backlog_summary_string_called = False
        self.get_blocked_summary_string_called = False
        self.get_active_string_response = ""
        self.get_backlog_summary_string_response = ""
        self.get_blocked_summary_string_response = ""

    def set_get_active_string_response(self, resp):
        self.get_active_string_response = resp

    def get_active_string(self):
        self.get_active_string_called = True
        return self.get_active_string_response

    def set_get_backlog_summary_string_response(self, resp):
        self.get_backlog_summary_string_response = resp

    def get_backlog_summary_string(self):
        self.get_backlog_summary_string_called = True
        return self.get_backlog_summary_string_response

    def set_get_blocked_summary_string_response(self, resp):
        self.get_blocked_summary_string_response = resp

    def get_blocked_summary_string(self):
        self.get_blocked_summary_string_called = True
        return self.get_blocked_summary_string_response

class TskDouble:
    def __init__(self):
        self.set_blocked_called = False
        self.set_blocked_reason = None
        self.set_blocked_id = None
        self.add_called = False
        self.add_summary = None
        self.add_description = None

    def set_blocked(self, id, reason):
        self.set_blocked_called = True
        self.set_blocked_id = id
        self.set_blocked_reason = reason
        return id == 10

    def add(self, summary, description=""):
        self.add_called = True
        self.add_summary = summary
        self.add_description = description
        return (True, 1)

class TskFrontEndTest(unittest.TestCase):
    def setUp(self):
        self.dbl1 = TskTextRenderDouble()
        self.dbl1.set_get_active_string_response("Active\n")
        self.dbl1.set_get_blocked_summary_string_response("Blocked\n")
        self.dbl1.set_get_backlog_summary_string_response("Backlog\n")
        self.dbl2 = PomoRenderDouble()
        self.dbl2.set_get_status_string_response("Pomo\n")
        self.tsk = TskDouble()

        self.fe = TskFrontEnd(self.tsk, self.dbl1, self.dbl2)

    def test_add_task(self):
        msg = self.fe.add_task("Task1Summary", "Task1Description")
        self.assertEquals("Task 1 added.", msg)

    def test_status(self):
        resp = self.fe.status()

        self.assertEquals("Pomo\nActive\nBlocked\nBacklog\n", resp)
        self.assertTrue(self.dbl1.get_active_string_called)
        self.assertTrue(self.dbl1.get_blocked_summary_string_called)
        self.assertTrue(self.dbl1.get_backlog_summary_string_called)
        self.assertTrue(self.dbl2.get_status_string_called)

    def test_backlog(self):
        resp = self.fe.backlog()

        self.assertEquals("Backlog\n", resp)

    def test_block(self):
        ret = self.fe.block(10, "MyReason")
        self.assertTrue(self.tsk.set_blocked_called)
        self.assertEquals("MyReason", self.tsk.set_blocked_reason)
        self.assertEquals(10, self.tsk.set_blocked_id)
        self.assertEquals("Task 10 marked blocked.", ret)

    def test_block_fail(self):
        ret = self.fe.block(11, "MyReason")
        self.assertTrue(self.tsk.set_blocked_called)
        self.assertEquals("Failed to mark task 11 blocked.", ret)

    def test_open(self):
        None

    def test_open_fail(self):
        None

    def test_close(self):
        None

    def test_close_fail(self):
        None

    def test_start(self):
        None

    def test_start_fail(self):
        None

    def test_cancel(self):
        None

    def test_cancel_fail(self):
        None

    def test_pause(self):
        None

    def test_pause_fail(self):
        None

    # def test_edit_task(self):
    #     self.fe.add_task("Task1Summary", "Task1Description")
    #     self.fe.edit_task(1)

if __name__ == '__main__':
    unittest.main()

