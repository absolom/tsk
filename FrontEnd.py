import os
import unittest
from TaskFileParser import TaskFileParser
from Render import TskTextRender, PomoRender
from OpenDouble import OpenDouble
from FileDouble import FileDouble
from TimeDouble import TimeDouble

class TskFrontEnd:
    def __init__(self, tsk=None, pomo=None, renderTsk=None, renderPomo=None,
                 time=None, subprocess=None, fileParser=None):
        self.tsk = tsk
        self.pomo = pomo
        self.renderTsk = renderTsk
        self.renderPomo = renderPomo
        self.time = time
        self.subprocess = subprocess
        self.fileParser = fileParser

        self.backlog_max_status = 20
        self.backlog_max = 10000000
        self.renderTsk.set_backlog_max(self.backlog_max_status)

        self.closed_max_status = 20
        self.closed_max = 45
        self.renderTsk.set_closed_max(self.closed_max_status)

    def set_due_date(self, id, date):
        task = self.tsk.get_task(id)
        return "Direct due date setting is unimplemented."

        if not task:
            return "Task {:d} could not be found.".format(id)

        return "Task {:d}'s due date has been set.".format(id)

    def edit_task(self, id):
        filename = '/tmp/tsk.tmp'
        if id is None:
            id = self.tsk.get_active()
            if id is None:
                return "Please provide a task id."
        task = self.tsk.get_task(id)
        if not task:
            return "Task {:d} could not be found.".format(id)
        self.fileParser.set_filename(filename)
        if not self.fileParser.create_file(task.summary, task.description):
            return "Temp file could not be created."
        time_start = self.time.time()
        if self.subprocess.call('vim {:s}'.format(filename), shell=True) != 0:
            return "Editor could not be invoked."
        if not self.fileParser.load_file():
            return "Temp file could not be loaded."
        if not self.fileParser.parse():
            return "Temp file could not be parsed."
        time_spent = self.time.time() - time_start
        task.log_time(time_spent)
        task.summary = self.fileParser.summary
        task.description = self.fileParser.description
        return "Task {:d} has been updated.".format(id)

    def add_task(self, summary, description):
        ret , id = self.tsk.add(summary, description)
        return "Task {:d} added.".format(id)

    def show_task(self, id):
        return self.renderTsk.get_task_string(id)

    def status(self):
        ret = os.linesep + self.renderPomo.get_status_string(self.time.time()) + os.linesep
        ret += self.renderTsk.get_active_string() + os.linesep + os.linesep
        ret += self.renderTsk.get_blocked_summary_string() + os.linesep + os.linesep
        ret += self.renderTsk.get_backlog_summary_string() + os.linesep
        return ret

    def closed(self):
        self.renderTsk.set_closed_max(self.closed_max)
        ret = "\n" + self.renderTsk.get_closed_summary_string()
        self.renderTsk.set_closed_max(self.closed_max_status)
        return ret

    def backlog(self):
        self.renderTsk.set_backlog_max(self.backlog_max)
        ret = self.renderTsk.get_backlog_summary_string()
        self.renderTsk.set_backlog_max(self.backlog_max_status)
        return ret

    def start(self):
        if self.pomo.start(self.time.time()):
            return "Pomodoro timer started."
        else:
            return "Pomodoro timer cannot be started."

    def pause(self):
        if self.pomo.pause(self.time.time()):
            return "Pomodoro timer paused."
        else:
            return "Pomodoro timer cannot be paused."

    def cancel(self):
        if self.pomo.cancel():
            return "Pomodoro timer canceled."
        else:
            return "Pomodoro timer could not be canceled."

    def monitor(self):
        while self.pomo.monitor(self.time.time()):
            self.time.sleep(1)

#### Test Doubles

openDouble = OpenDouble()
if __name__ == '__main__':
    open = openDouble

#### Test Code

from TskTextRenderDouble import TskTextRenderDouble
from PomoRenderDouble import PomoRenderDouble
from TskDouble import TskDouble
from PomoDouble import PomoDouble
from SubprocessDouble import SubprocessDouble
from TaskFileParserDouble import TaskFileParserDouble

class TskFrontEndTest(unittest.TestCase):
    def setUp(self):
        self.dbl1 = TskTextRenderDouble()
        self.dbl1.set_get_active_string_response("Active\n")
        self.dbl1.set_get_blocked_summary_string_response("Blocked\n")
        self.dbl1.set_get_backlog_summary_string_response("Backlog\n")
        self.dbl1.set_get_closed_summary_string_response("Closed\n")
        self.dbl2 = PomoRenderDouble()
        self.dbl2.set_get_status_string_response("Pomo\n")
        self.tsk = TskDouble()
        self.pomo = PomoDouble()
        self.time = TimeDouble()

        self.fe = TskFrontEnd(self.tsk, self.pomo, self.dbl1, self.dbl2, self.time, None, None)

    def test_sets_backlog_max(self):
        self.assertTrue(self.dbl1.set_backlog_max_called[0])

    def test_add_task(self):
        msg = self.fe.add_task("Task1Summary", "Task1Description")
        self.assertEquals("Task 1 added.", msg)

    def test_status(self):
        resp = self.fe.status()

        self.assertEquals(os.linesep + "Pomo" + 2*os.linesep + "Active"
            + 3*os.linesep + "Blocked" + 3*os.linesep + "Backlog" + 2*os.linesep, resp)
        self.assertTrue(self.dbl1.get_active_string_called)
        self.assertTrue(self.dbl1.get_blocked_summary_string_called)
        self.assertTrue(self.dbl1.get_backlog_summary_string_called)
        self.assertTrue(self.dbl2.get_status_string_called)

    def test_backlog(self):
        self.dbl1.set_backlog_max_called = []
        self.dbl1.set_backlog_max_max = []
        resp = self.fe.backlog()

        self.assertEquals("Backlog\n", resp)
        self.assertEquals(2, len(self.dbl1.set_backlog_max_called))
        self.assertEquals(self.fe.backlog_max, self.dbl1.set_backlog_max_max[0])
        self.assertEquals(self.fe.backlog_max_status, self.dbl1.set_backlog_max_max[1])

    def test_closed(self):
        self.dbl1.set_closed_max_called = []
        self.dbl1.set_closed_max_max = []
        resp = self.fe.closed()

        self.assertEquals("\nClosed\n", resp)
        self.assertEquals(2, len(self.dbl1.set_closed_max_called))
        self.assertEquals(self.fe.closed_max, self.dbl1.set_closed_max_max[0])
        self.assertEquals(self.fe.closed_max_status, self.dbl1.set_closed_max_max[1])

class TskFrontEndTest_EditCommand(unittest.TestCase):
    def setUp(self):
        self.dbl1 = TskTextRenderDouble()
        self.dbl1.set_get_active_string_response("Active\n")
        self.dbl1.set_get_blocked_summary_string_response("Blocked\n")
        self.dbl1.set_get_backlog_summary_string_response("Backlog\n")
        self.dbl2 = PomoRenderDouble()
        self.dbl2.set_get_status_string_response("Pomo\n")
        self.tsk = TskDouble()
        self.pomo = PomoDouble()
        self.time = TimeDouble()
        self.fileDouble = FileDouble()
        self.fileDoubleEdited = FileDouble()
        self.subprocess = SubprocessDouble()
        openDouble.reset()
        openDouble.add_file(self.fileDouble)
        openDouble.add_file(self.fileDoubleEdited)
        self.tfpDouble = TaskFileParserDouble()

        self.fe = TskFrontEnd(self.tsk, self.pomo, self.dbl1, self.dbl2,
                              self.time, self.subprocess, self.tfpDouble)

    def test_edit_task_creates_temp_file(self):
        self.fe.add_task("Task1Summary", "Task1Description")
        ret = self.fe.edit_task(1)
        self.assertTrue(self.tfpDouble.set_filename_called)
        self.assertEquals('/tmp/tsk.tmp', self.tfpDouble.set_filename_filename)
        self.assertTrue(self.tfpDouble.create_file_called)
        self.assertEquals("Task1Summary", self.tfpDouble.create_file_summary)
        self.assertEquals("Task1Description", self.tfpDouble.create_file_description)
        self.assertEquals("Task 1 has been updated.", ret)

    def test_edit_task_logs_time(self):
        self.time.add_time(100)
        self.fe.add_task("Task1Summary", "Task1Description")
        ret = self.fe.edit_task(1)
        self.assertEquals(100, self.tsk.task.log_time_param)

    def test_edit_invalid_id(self):
        ret = self.fe.edit_task(10)
        self.assertEquals("Task 10 could not be found.", ret)

    def test_edit_launches_editor(self):
        self.fe.add_task("Task1Summary", "Task1Description")
        self.fe.edit_task(1)
        self.assertEquals("vim /tmp/tsk.tmp", self.subprocess.call_command)
        self.assertTrue(self.subprocess.call_shell)

    def test_edit_opens_tmp_file_post_edit(self):
        self.fe.add_task("Task1Summary", "Task1Description")
        self.fe.edit_task(1)
        self.assertTrue(self.tfpDouble.load_file_called)
        self.assertTrue(self.tfpDouble.parse_called)

    def test_edit_updates_task(self):
        self.tfpDouble.set_summary("MySummary")
        self.tfpDouble.set_description("MyDescription")
        self.fe.add_task("Task1Summary", "Task1Description")
        self.fe.edit_task(1)
        self.assertEquals("MySummary", self.tsk.task.summary)
        self.assertEquals("MyDescription", self.tsk.task.description)

    def test_edit_vim_not_found(self):
        self.subprocess.set_call_fail()
        self.fe.add_task("Task1Summary", "Task1Description")
        ret = self.fe.edit_task(1)
        self.assertEquals("Editor could not be invoked.", ret)

    def test_edit_file_create_fails(self):
        self.tfpDouble.set_create_file_fail()
        self.fe.add_task("Task1Summary", "Task1Description")
        ret = self.fe.edit_task(1)
        self.assertEquals("Temp file could not be created.", ret)

    def test_edit_file_load_fails(self):
        self.tfpDouble.set_load_file_fail()
        self.fe.add_task("Task1Summary", "Task1Description")
        ret = self.fe.edit_task(1)
        self.assertEquals("Temp file could not be loaded.", ret)

    def test_edit_file_parse_fails(self):
        self.tfpDouble.set_parse_fail()
        self.fe.add_task("Task1Summary", "Task1Description")
        ret = self.fe.edit_task(1)
        self.assertEquals("Temp file could not be parsed.", ret)

class TskFrontEndPomoTest(unittest.TestCase):
    def setUp(self):
        self.dbl1 = TskTextRenderDouble()
        self.dbl1.set_get_active_string_response("Active\n")
        self.dbl1.set_get_blocked_summary_string_response("Blocked\n")
        self.dbl1.set_get_backlog_summary_string_response("Backlog\n")
        self.dbl2 = PomoRenderDouble()
        self.dbl2.set_get_status_string_response("Pomo\n")
        self.tsk = TskDouble()
        self.pomo = PomoDouble()
        self.time = TimeDouble()

        self.fe = TskFrontEnd(self.tsk, self.pomo,  self.dbl1, self.dbl2, self.time)

    def test_start(self):
        ret = self.fe.start()
        self.assertEquals("Pomodoro timer started.", ret)

    def test_start_fail(self):
        self.pomo.set_start_fail()
        ret = self.fe.start()
        self.assertEquals("Pomodoro timer cannot be started.", ret)

    def test_start_correct_time(self):
        self.time.set_time(1)
        self.fe.start()
        self.assertEquals(1, self.pomo.start_time)

    def test_pause(self):
        ret = self.fe.pause()
        self.assertEquals("Pomodoro timer paused.", ret)

    def test_pause_correct_time(self):
        self.time.set_time(2)
        self.fe.pause()
        self.assertEquals(2, self.pomo.pause_time)

    def test_pause_fail(self):
        self.pomo.set_pause_fail()
        ret = self.fe.pause()
        self.assertEquals("Pomodoro timer paused.", ret)

    def test_cancel(self):
        ret = self.fe.cancel()
        self.assertEquals("Pomodoro timer canceled.", ret)

    def test_cancel_cancels(self):
        self.fe.cancel()
        self.assertTrue(self.pomo.canceled)

    def test_cancel_fails(self):
        self.pomo.set_cancel_fail()
        ret = self.fe.cancel()
        self.assertEquals("Pomodoro timer could not be canceled.", ret)

    def test_monitor(self):
        self.time.set_time(0)
        self.pomo.set_monitor_count(5)
        self.fe.monitor()
        self.assertEquals(4, self.time.time())

if __name__ == '__main__':
    unittest.main()
