import unittest
import math
from TskLogic import TskLogic
from Pomo import Pomo

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

class StringsTest(unittest.TestCase):
    def setUp(self):
        self.tsk = TskLogic()
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
        self.tskfe = TskTextRender(TskLogic())
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

if __name__ == '__main__':
    unittest.main()