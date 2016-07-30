import unittest
import time

class Task:
    def __init__(self, summary, description, createDate=time.time()):
        self.summary = summary
        self.description = description
        self.blocked_reason = None
        self.closed_reason = None
        self.id = None
        self.state = "Open"
        self.date_created = createDate
        self.date_closed = None
        self.date_due = None
        self.time_estimate = 0
        self.time_spent = 0

    def __eq__(self, other):
        return self.summary == other.summary and self.description == other.description

    def set_estimate(self, estimate):
        self.time_estimate = estimate

    def log_time(self, t):
        self.time_spent += t

    def set_due_date(self, epochT):
        self.date_due = epochT

    def remove_due_date(self):
        self.date_due = None

    def is_active(self):
        return self.state == "Active"

    def is_blocked(self):
        return self.state == "Blocked"

    def is_closed(self):
        return self.state == "Closed"

    def is_open(self):
        return self.state == "Open"

    def close(self, t=time.time(), reason=None):
        self.blocked_reason = None
        self.closed_reason = reason
        self.state = "Closed"
        self.date_closed = t

    def open(self):
        self.blocked_reason = None
        self.closed_reason = None
        self.state = "Open"
        return True

    def block(self, reason):
        self.state = "Blocked"
        self.blocked_reason = reason
        self.closed_reason = None
        return True

    def activate(self):
        self.blocked_reason = None
        self.closed_reason = None
        self.state = "Active"
        return True

class TaskTest(unittest.TestCase):
    def setUp(self):
        self.task = Task("Task1", "")

    def _verifyState(self, truthState):
        states = ["closed", "open", "blocked", "active"]
        for state in states:
            if state == truthState:
                self.assertTrue(eval("self.task.is_" + state + "()"))
            else:
                self.assertFalse(eval("self.task.is_" + state + "()"))

    def test_default_is_open(self):
        self.assertTrue(self.task.is_open())

    def test_close_task(self):
        self.task.close(t=1000, reason="MyReason")

        self._verifyState("closed")
        self.assertIsNone(self.task.blocked_reason)
        self.assertEquals(1000, self.task.date_closed)
        self.assertEquals("MyReason", self.task.closed_reason)

    def test_open_task(self):
        self.task.open()

        self._verifyState("open")
        self.assertIsNone(self.task.blocked_reason)
        self.assertIsNone(self.task.closed_reason)

    def test_block_task(self):
        self.task.block("BlockReason")

        self._verifyState("blocked")
        self.assertEquals("BlockReason", self.task.blocked_reason)
        self.assertIsNone(self.task.closed_reason)

    def test_activate_task(self):
        self.task.activate()

        self._verifyState("active")
        self.assertIsNone(self.task.blocked_reason)
        self.assertIsNone(self.task.closed_reason)

    def test_create_date(self):
        self.task = Task("Summary", "Description", 1001)
        self.assertEquals(1001, self.task.date_created)

    def test_close_date_none_default(self):
        self.assertIsNone(self.task.date_closed)

if __name__ == '__main__':
    unittest.main()