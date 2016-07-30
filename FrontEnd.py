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
        self.backlog_max = 45
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

    def set_due_date_relative(self, id, day_offset):
        task = self.tsk.get_task(id)
        if not task:
            return "Task {:d} could not be found.".format(id)

        seconds_offset = day_offset * 24 * 60 * 60
        task.set_due_date(self.time.time() + seconds_offset)

        return "Task {:d}'s due date has been set.".format(id)
    def remove_due_date(self, id, date):
        task = self.tsk.get_task(id)
        if not task:
            return "Task {:d} could not be found.".format(id)
        task.remove_due_date()
        return "Task {:d}'s due date has been removed.".format(id)

    def edit_task(self, id):
        filename = '/tmp/tsk.tmp'
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

    def block(self, id, reason):
        if self.tsk.set_blocked(id, reason):
            return "Task {:d} marked blocked.".format(id)

        return "Failed to mark task {:d} blocked.".format(id)

    def set_position(self, id, pos):
        if self.tsk.set_backlog_position(id, pos):
            return "Task {:d} moved to position {:d}.".format(id, pos)

        return "Failed to move task {:d}.".format(id)

    def set_position_relative(self, id, offset):
        if self.tsk.set_backlog_position_relative(id, offset):
            if offset >= 0:
                return "Task {:d} moved {:d} up.".format(id, offset)
            else:
                return "Task {:d} moved {:d} down.".format(id, offset)

        return "Failed to move task {:d}.".format(id)

    def open(self, id):
        if self.tsk.set_open(id):
            return "Task {:d} opened.".format(id)

        return "Failed to open task {:d}.".format(id)

    def close(self, id, reason):
        if self.tsk.set_closed(id, reason):
            return "Task {:d} closed.".format(id)

        return "Failed to close task {:d}.".format(id)

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

    def activate(self, id):
        if self.tsk.set_active(id):
            return "Task {:d} activated.".format(id)
        else:
            return "Failed to activate task {:d}.".format(id)

    def monitor(self):
        while self.pomo.monitor(self.time.time()):
            self.time.sleep(1)

    def time_estimate(self, id, estimate):
        task = self.tsk.get_task(id)
        if task is None:
            return "Task {:d} could not be found.".format(id)

        task.set_estimate(estimate)
        return "Estimate set for Task {:d}.".format(id)

    def time_log(self, id, t):
        task = self.tsk.get_task(id)
        if task is None:
            return "Task {:d} could not be found.".format(id)

        task.log_time(t)
        return "Time recorded for Task {:d}.".format(id)

    def sort_backlog(self, secondarySort):
        self.tsk.sort_backlog(secondarySort)
        return "Backlog sorted by due date."

#### Test Doubles

class TaskFileParserDouble:
    def __init__(self):
        self.summary = None
        self.description = None
        self.set_filename_called = False
        self.create_file_called = False
        self.load_file_called = False
        self.parse_called = False
        self.set_filename_filename = None
        self.create_file_fail = False
        self.load_file_fail = False
        self.parse_fail = False

    def set_filename(self, filename):
        self.set_filename_called = True
        self.set_filename_filename = filename

    def create_file(self, summary, description):
        self.create_file_called = True
        self.create_file_summary = summary
        self.create_file_description = description
        return not self.create_file_fail

    def load_file(self):
        self.load_file_called = True
        return not self.load_file_fail

    def parse(self):
        self.parse_called = True
        return not self.parse_fail

    def set_summary(self, summary):
        self.summary = summary

    def set_description(self, description):
        self.description = description

    def set_create_file_fail(self):
        self.create_file_fail = True

    def set_load_file_fail(self):
        self.load_file_fail = True

    def set_parse_fail(self):
        self.parse_fail = True

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
        self.get_closed_summary_string_called = False
        self.get_active_string_response = ""
        self.get_backlog_summary_string_response = ""
        self.get_blocked_summary_string_response = ""
        self.get_closed_summary_string_response = ""
        self.set_backlog_max_max = []
        self.set_backlog_max_called = []
        self.set_closed_max_max = []
        self.set_closed_max_called = []

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

    def set_get_closed_summary_string_response(self, resp):
        self.get_closed_summary_string_response = resp

    def get_closed_summary_string(self):
        self.get_closed_summary_string_called = True
        return self.get_closed_summary_string_response

    def set_backlog_max(self, max):
        self.set_backlog_max_called.append(True)
        self.set_backlog_max_max.append(max)

    def set_closed_max(self, max):
        self.set_closed_max_called.append(True)
        self.set_closed_max_max.append(max)

class TskDouble:
    class TaskDouble:
        def __init__(self, summary, description):
            self.summary = summary
            self.description = description
            self.set_due_date_relative_offset = None

        def set_due_date(self, due_date_offset):
            self.set_due_date_relative_offset = due_date_offset
            return True

        def log_time(self, t):
            self.log_time_param = t

    def __init__(self):
        self.set_blocked_called = False
        self.set_blocked_reason = None
        self.set_blocked_id = None
        self.add_called = False
        self.add_summary = None
        self.add_description = None
        self.task = None
        self.get_task_id = None

    def set_blocked(self, id, reason):
        self.set_blocked_called = True
        self.set_blocked_id = id
        self.set_blocked_reason = reason
        return id == 10

    def add(self, summary, description=""):
        self.add_called = True
        self.add_summary = summary
        self.add_description = description
        self.task = self.TaskDouble(summary, description)
        return (True, 1)

    def set_active(self, id):
        return id == 10

    def set_open(self, id):
        return id == 10

    def set_closed(self, id, reason):
        return id == 10 and reason == "Reason"

    def get_task(self, id):
        self.get_task_id = id
        return self.task

class PomoDouble:
    def __init__(self):
        self.start_fail = False
        self.start_time = None
        self.pause_fail = False
        self.pause_time = None
        self.canceled = False
        self.cancel_fail = False
        self.monitor_count = 0

    def set_start_fail(self):
        self.start_fail = True

    def set_pause_fail(self):
        self.pause_fail = True

    def set_cancel_fail(self):
        self.cancel_fail = True

    def start(self, t):
        self.start_time = t
        return not self.start_fail

    def pause(self, t):
        self.pause_time = t
        return True

    def cancel(self):
        self.canceled = True
        return not self.cancel_fail

    def set_monitor_count(self, cnt):
        self.monitor_count = cnt

    def monitor(self, t):
        self.monitor_count -= 1
        return self.monitor_count > 0

class SubprocessDouble:
    def __init__(self):
        self.call_command = None
        self.vim_edits = None
        self.call_fail = False

    def call(self, command, shell=None):
        self.call_command = command
        self.call_shell = shell
        if self.call_fail:
            return 1
        return 0

    def set_call_fail(self):
        self.call_fail = True

class WriteDouble:
    def __init__(self):
        self.written_data = ""

    def __call__(self, ):
        self.filename = filename
        self.mode = mode

openDouble = OpenDouble()
if __name__ == '__main__':
    open = openDouble

#### Test Code

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
        ret = self.fe.open(10)
        self.assertEquals("Task 10 opened.", ret)

    def test_open_fail(self):
        ret = self.fe.open(11)
        self.assertEquals("Failed to open task 11.", ret)

    def test_close(self):
        ret = self.fe.close(10, "Reason")
        self.assertEquals("Task 10 closed.", ret)

    def test_close_fail(self):
        ret = self.fe.close(11, "Reason")
        self.assertEquals("Failed to close task 11.", ret)

    def test_activate(self):
        ret = self.fe.activate(10)
        self.assertEquals("Task 10 activated.", ret)

    def test_activate_fail(self):
        ret = self.fe.activate(11)
        self.assertEquals("Failed to activate task 11.", ret)

    def test_set_due_date_relative(self):
        self.tsk.add("Summary", "Description")
        self.time.set_time(1000)
        ret = self.fe.set_due_date_relative(10, 1)
        self.assertEquals("Task 10's due date has been set.", ret)
        self.assertEquals(1000+24*60*60, self.tsk.task.set_due_date_relative_offset)

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
