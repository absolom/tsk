import unittest
import math
from TskLogic import TskLogic
from Pomo import Pomo
from datetime import datetime

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

class TskTextRender:
    def __init__(self, tsk, datetime=datetime):
        self.tsk = tsk
        self.backlog_max = 4
        self.blocked_max = 10
        self.closed_max = 20
        self.datetime = datetime

    def _task_to_string(self, task):
        # TODO: Probably push this into Task eventually
        return "{:<3d}   {:s}\n{:s}".format(task.id, task.summary, task.description)

    def get_active_string(self):
        if self.tsk.get_active() == None:
            return "No Active Task."

        active_task = self.tsk.get_task(self.tsk.get_active())
        return "{:s}\n{:s}".format("Active Task", self._task_to_string(active_task))

    def get_task_string(self, id):
        task = self.tsk.get_task(id)
        if task is None:
            return "Task {:d} not found.".format(id)

        return self._task_to_string(task)

    # TODO: All the get_*_summary_string() functions need duplication removed
    def get_backlog_summary_string(self):
        ret = "Backlog"
        output = 0
        num_in_backlog = 0
        for i, task in enumerate(self.tsk.list_tasks()):
            if not task.is_open():
                continue
            num_in_backlog += 1

        for i, task in enumerate(self.tsk.list_tasks()):
            if not task.is_open():
                continue

            ret += "\n{:<3d}   {:s}".format(task.id, task.summary)
            output += 1
            if output >= self.backlog_max:
                ret += "\n... {:d} More".format(num_in_backlog - output)
                break

        return ret

    def get_closed_summary_string(self):
        ret = "Closed"
        output = 0
        num_closed = 0
        for i, task in enumerate(self.tsk.list_tasks()):
            if not task.is_closed():
                continue
            num_closed += 1

        for i, task in enumerate(self.tsk.list_tasks()):
            if not task.is_closed():
                continue

            closed_date = datetime.fromtimestamp(task.date_closed)
            closed_date_string = closed_date.strftime('%m-%d-%y')
            ret += "\n{:<3d}   {:s} : {:s}".format(task.id, closed_date_string, task.summary)
            output += 1
            if output >= self.closed_max:
                ret += "\n... {:d} More".format(num_closed - output)
                break

        return ret


    def get_blocked_summary_string(self):
        ret = "Blocked"
        output = 0
        num_blocked = 0
        for i, task in enumerate(self.tsk.list_tasks()):
            if not task.is_blocked():
                continue
            num_blocked += 1

        for i, task in enumerate(self.tsk.list_tasks()):
            if not task.is_blocked():
                continue

            ret += "\n{:<3d}   {:s}\n          {:s}".format(task.id, task.summary, task.blocked_reason)
            output += 1
            if output >= self.blocked_max:
                ret += "\n... {:d} More".format(num_blocked - output)
                break

        return ret

    def set_backlog_max(self, max):
        self.backlog_max = max

    def set_blocked_max(self, max):
        self.blocked_max = max

class StringsTest(unittest.TestCase):
    def setUp(self):
        self.tsk = TskLogic()
        self.tsk.add("Task1")
        self.tsk.add("Task2", "Task2 Description")
        self.tsk.add("Task3")
        self.tsk.add("Task4", "Task4 Description")

        for i in range(5, 25):
            self.tsk.add("Task%d" % i)

        self.tskfe = TskTextRender(self.tsk)
        self.tskfe.set_backlog_max(4)
        self.tskfe.set_blocked_max(4)

    def test_get_task_string(self):
        truth = """2     Task2\nTask2 Description"""
        self.assertEquals(truth, self.tskfe.get_task_string(2))

    def test_get_task_string_no_task(self):
        truth = "Task 30 not found."
        self.assertEquals(truth, self.tskfe.get_task_string(30))

    def test_get_active_string_no_active(self):
        status_active_truth = """No Active Task."""
        self.assertEquals(status_active_truth, self.tskfe.get_active_string())

    def test_get_active_string_with_active(self):
        self.tsk.set_active(1)
        status_active_truth = """Active Task
1     Task1\n"""
        self.assertEquals(status_active_truth, self.tskfe.get_active_string())

    def test_get_active_string_with_active_and_description(self):
        self.tsk.set_active(2)
        status_active_truth = """Active Task
2     Task2
Task2 Description"""
        self.assertEquals(status_active_truth, self.tskfe.get_active_string())

    def test_get_backlog_summary(self):
        self.tsk = TskLogic()
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
5     Task5
... 19 More"""
        self.tskfe.set_backlog_max(5)
        self.assertEquals(backlog_truth, self.tskfe.get_backlog_summary_string())

    def test_get_backlog_summary_with_active(self):
        self.tsk.set_active(3)
        backlog_truth = """Backlog
1     Task1
2     Task2
4     Task4
5     Task5
... 19 More"""
        self.assertEquals(backlog_truth, self.tskfe.get_backlog_summary_string())

    def test_get_backlog_summary_none(self):
        self.tskfe = TskTextRender(TskLogic())
        self.assertEquals("Backlog", self.tskfe.get_backlog_summary_string())

    def test_get_backlog_summary_skips_closed(self):
        self.tsk.set_closed(3)
        self.tsk.set_closed(5)
        self.tsk.set_closed(21)
        backlog_truth = """Backlog
1     Task1
2     Task2
4     Task4
6     Task6
... 17 More"""
        self.assertEquals(backlog_truth, self.tskfe.get_backlog_summary_string())

    def test_get_backlog_summary_skips_blocked(self):
        self.tsk.set_blocked(3, "Reason")
        self.tsk.set_blocked(5, "Reason")
        self.tsk.set_blocked(21, "Reason")
        backlog_truth = """Backlog
1     Task1
2     Task2
4     Task4
6     Task6
... 17 More"""
        self.assertEquals(backlog_truth, self.tskfe.get_backlog_summary_string())

    def test_get_blocked_status(self):
        self.tsk.set_blocked(3, "Reason1")
        self.tsk.set_blocked(5, "Reason2")
        blocked_truth = """Blocked
3     Task3
          Reason1
5     Task5
          Reason2"""
        self.assertEquals(blocked_truth, self.tskfe.get_blocked_summary_string())

    def test_get_blocked_status_empty(self):
        blocked_truth = """Blocked"""
        self.assertEquals(blocked_truth, self.tskfe.get_blocked_summary_string())

    def test_get_blocked_status_overflow(self):
        for i in range(1,15):
            self.tsk.set_blocked(i, "Reason{:d}".format(i))
        self.tsk.set_open(2)
        blocked_truth = """Blocked
1     Task1
          Reason1
3     Task3
          Reason3
4     Task4
          Reason4
5     Task5
          Reason5
... 9 More"""
        self.assertEquals(blocked_truth, self.tskfe.get_blocked_summary_string())

    def test_get_blocked_status_overflow_different_max(self):
        for i in range(1,15):
            self.tsk.set_blocked(i, "Reason{:d}".format(i))
        self.tskfe.set_blocked_max(2)
        blocked_truth = """Blocked
1     Task1
          Reason1
2     Task2
          Reason2
... 12 More"""
        self.assertEquals(blocked_truth, self.tskfe.get_blocked_summary_string())

    def test_get_closed_status(self):
        self.tsk.set_closed(3)
        self.tsk.set_closed(5)
        self.tsk.get_task(3).date_closed = 1
        self.tsk.get_task(5).date_closed = 3600*24 + 1
        closed_truth = """Closed
3     12-31-69 : Task3
5     01-01-70 : Task5"""
        self.assertEquals(closed_truth, self.tskfe.get_closed_summary_string())

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

if __name__ == '__main__':
    unittest.main()