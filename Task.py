import unittest
import time

class Task:
    def __init__(self, summary, description, createDate=time.time()):
        self.summary = summary
        self.description = description
        self.blocked_reason = None
        self.id = None
        self.state = "Open"
        self.date_created = createDate
        self.date_closed = None
        self.date_due = None
        self.pomo_estimate = None
        self.pomo_completed = 0

    def __eq__(self, other):
        return self.summary == other.summary and self.description == other.description

    def set_estimate(self, pomos):
        self.pomo_estimate = pomos

    def record_work(self):
        self.pomo_completed += 1

    def set_due_date(self, epochT):
        self.date_due = epochT

    def remove_due_date(self, epochT):
        self.date_due = None

    def is_active(self):
        return self.state == "Active"

    def is_blocked(self):
        return self.state == "Blocked"

    def is_closed(self):
        return self.state == "Closed"

    def is_open(self):
        return self.state == "Open"

    def close(self, t=time.time()):
        self.blocked_reason = None
        self.state = "Closed"
        self.date_closed = t

    def open(self):
        self.blocked_reason = None
        self.state = "Open"
        return True

    def block(self, reason):
        self.state = "Blocked"
        self.blocked_reason = reason
        return True

    def activate(self):
        self.blocked_reason = None
        self.state = "Active"
        return True

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
        self.assertIsNone(self.task.blocked_reason)

    def test_blocked_to_closed(self):
        self.task.block("Reason")
        self.task.close()
        self.assertFalse(self.task.is_blocked())
        self.assertTrue(self.task.is_closed())
        self.assertIsNone(self.task.blocked_reason)

    def test_blocked_to_active(self):
        self.task.block("Reason")
        self.task.activate()
        self.assertFalse(self.task.is_blocked())
        self.assertTrue(self.task.is_active())
        self.assertIsNone(self.task.blocked_reason)

    def test_active_to_closed(self):
        self.task.activate()
        self.task.close()
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

    def test_create_date(self):
        self.task = Task("Summary", "Description", 1001)
        self.assertEquals(1001, self.task.date_created)

    def test_close_date(self):
        self.task.close(1111)
        self.assertEquals(1111, self.task.date_closed)

    def test_close_date_none_default(self):
        self.assertIsNone(self.task.date_closed)

if __name__ == '__main__':
    unittest.main()