import unittest
import math
import os
import time
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

    def _get_estimate_string(self, task):
        estimate_string = ''
        if task.pomo_estimate is not None:
            estimate_string = " ({:d}/{:d})".format(task.pomo_completed, task.pomo_estimate)
        elif task.pomo_completed > 0:
            estimate_string = " ({:d})".format(task.pomo_completed)
        return estimate_string

    def _task_to_string(self, task, showDescription=True):
        # TODO: Probably push this into Task eventually
        estimate_string = self._get_estimate_string(task)

        ret = ''
        if showDescription:
            ret = "{:<3d}   {:s}{:s}{:s}{:s}".format(task.id, task.summary, estimate_string, 2*os.linesep, task.description)
        else:
            ret = "{:<3d}   {:s}{:s}".format(task.id, task.summary, estimate_string)
        return ret

    def _get_due_date_string(self, task, t):
        dueDateString = ' '
        if not task.date_due is None:
            if task.date_due < t:
                dueDateString = '!'
            elif task.date_due - t < 60*60*24:
                dueDateString = '^'
            elif task.date_due - t < 60*60*24*2:
                dueDateString = '>'
            elif task.date_due - t < 60*60*24*7:
                dueDateString = '~'
            elif task.date_due - t < 60*60*24*7*4:
                dueDateString = '-'
            else:
                dueDateString = '.'
        return dueDateString

    def _generate_summary_string(self, cb_include, cb_render, render_max):
        output = 0
        num_to_include = 0
        ret = ''

        for i, task in enumerate(self.tsk.list_tasks()):
            if not cb_include(task):
                continue
            num_to_include += 1

        for i, task in enumerate(self.tsk.list_tasks()):
            if not cb_include(task):
                continue

            ret += cb_render(task)

            output += 1
            if output == render_max and num_to_include - output > 0:
                ret += "\n... {:d} More".format(num_to_include - output)
                break

        return ret

    def get_active_string(self):
        if self.tsk.get_active() == None:
            return "No Active Task."

        active_task = self.tsk.get_task(self.tsk.get_active())
        return "{:s}\n{:s}".format("Active Task", self._task_to_string(active_task))

    def get_task_string(self, id):
        task = self.tsk.get_task(id)
        if task is None:
            return "Task {:d} not found.".format(id)

        return os.linesep + self._task_to_string(task)

    def get_backlog_summary_string(self, t=time.time()):

        def include_test(task):
            return task.is_open()

        def render(task):
            dueDateString = self._get_due_date_string(task, t)
            return "\n{:<3d} {:s} {:s}{:s}".format(task.id, dueDateString, task.summary, self._get_estimate_string(task))

        return "Backlog" + self._generate_summary_string(include_test, render, self.backlog_max)

    def get_closed_summary_string(self):

        def include_test(task):
            return task.is_closed()

        def render(task):
            closed_date = datetime.fromtimestamp(task.date_closed)
            closed_date_string = closed_date.strftime('%m-%d-%y')
            return "\n{:<3d}   {:s} : {:s}".format(task.id, closed_date_string, task.summary)

        return "Closed" + self._generate_summary_string(include_test, render, self.closed_max)

    def get_blocked_summary_string(self):

        def include_test(task):
            return task.is_blocked()

        def render(task):
            return  "\n{:<3d}   {:s}\n          {:s}".format(task.id, task.summary, task.blocked_reason)

        return "Blocked" + self._generate_summary_string(include_test, render, self.blocked_max)

    def set_backlog_max(self, mx):
        self.backlog_max = mx

    def set_blocked_max(self, mx):
        self.blocked_max = mx

    def set_closed_max(self, mx):
        self.closed_max = mx

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
        truth = """\n2     Task2\n\nTask2 Description"""
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
1     Task1\n\n"""
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

    def test_get_backlog_with_due_dates(self):
        self.tsk = TskLogic()
        self.tsk.add("Task1")
        self.tsk.add("Task2", "Task2 Description")
        self.tsk.add("Task3")
        self.tsk.add("Task4")
        self.tsk.add("Task5")

        self.tsk.get_task(1).date_due = 1
        self.tsk.get_task(2).date_due = 101
        self.tsk.get_task(3).date_due = 101 + 60*60*24
        self.tsk.get_task(4).date_due = 101 + 60*60*24*6
        self.tsk.get_task(5).date_due = 101 + 60*60*24*6*4

        self.tskfe = TskTextRender(self.tsk)
        self.tskfe.set_backlog_max(5)
        backlog_truth = """Backlog
1   ! Task1
2   ^ Task2
3   > Task3
4   ~ Task4
5   - Task5"""
        self.assertEquals(backlog_truth, self.tskfe.get_backlog_summary_string(100))

    def test_get_backlog_with_estimates(self):
        self.tsk = TskLogic()
        self.tsk.add("Task1")
        self.tsk.add("Task2", "Task2 Description")
        self.tsk.add("Task3")
        self.tsk.add("Task4")
        self.tsk.add("Task5")

        self.tsk.get_task(1).set_estimate(1)

        self.tsk.get_task(2).set_estimate(10)
        for i in range(0,4):
            self.tsk.get_task(2).log_work()

        self.tsk.get_task(3).log_work()
        self.tsk.get_task(3).log_work()

        self.tskfe = TskTextRender(self.tsk)
        self.tskfe.set_backlog_max(5)
        backlog_truth = """Backlog
1     Task1 (0/1)
2     Task2 (4/10)
3     Task3 (2)
4     Task4
5     Task5"""
        self.assertEquals(backlog_truth, self.tskfe.get_backlog_summary_string(100))

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

    def test_get_backlog_summary_overflow_edge(self):
        backlog_truth = """Backlog
1     Task1
2     Task2
3     Task3
4     Task4"""
        self.tsk = TskLogic()
        self.tsk.add("Task1")
        self.tsk.add("Task2")
        self.tsk.add("Task3")
        self.tsk.add("Task4")

        self.tskfe = TskTextRender(self.tsk)
        self.tskfe.set_backlog_max(4)
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