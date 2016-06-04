import unittest
import time
from TimeDouble import TimeDouble

class Pomo:
    def __init__(self):
        self.start_time = None
        self.running = False
        self.elapsed = 0.0

    def start(self, t):
        if not self.running:
            self.start_time = t
            self.running = True
            return True
        return False

    def set_remaining_time(self, t):
        self.elapsed = 25.0*60.0 - t

    def get_remaining_time(self, t):
        elapsed_this_lap = 0
        if self.running:
            elapsed_this_lap = t - self.start_time
        remaining_time = 25*60 - (self.elapsed + elapsed_this_lap)
        if remaining_time < 0:
            remaining_time = 0
        return remaining_time

    def pause(self, t):
        if self.running:
            self.elapsed += t - self.start_time
            self.running = False
            return True
        return False

    def cancel(self):
        self.__init__()
        return True

    def is_paused(self):
        return not self.running

    def is_expired(self, t):
        return self.get_remaining_time(t) <= 0

    def monitor(self, t):
        if not self.running:
            return False

        if self.get_remaining_time(t) == 0:
            return False

        return True

class PomoTest_Pause(unittest.TestCase):
    def setUp(self):
        self.pomo = Pomo()

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

class PomoTest_StartAndRun(unittest.TestCase):
    def setUp(self):
        self.pomo = Pomo()

    def test_remaining_time_default(self):
        self.assertEquals(25*60, self.pomo.get_remaining_time(time.time()))

    def test_remaining_time_decreases_correctly(self):
        self.pomo.start(0.0)
        self.assertEquals(25*60 - 3, self.pomo.get_remaining_time(3.0))

    def test_remaining_time_no_round_up(self):
        self.pomo.start(0.0)
        self.assertEquals(25*60 - 2.5, self.pomo.get_remaining_time(2.5))

    def test_remaining_time_no_rounds_down(self):
        self.pomo.start(0.0)
        self.assertEquals(25*60 - 3.49, self.pomo.get_remaining_time(3.49))

    def test_remaining_time_finished(self):
        self.pomo.start(0)
        self.assertEquals(0, self.pomo.get_remaining_time(25*60*2))

    def test_double_start(self):
        self.assertTrue(self.pomo.start(0.0))
        self.assertFalse(self.pomo.start(3.0))
        self.assertEquals(25*60 - 6, self.pomo.get_remaining_time(6.0))

    def test_set_remaining_time(self):
        self.pomo.set_remaining_time(10.1)
        self.assertAlmostEquals(10.1, self.pomo.get_remaining_time(0))

class PomoTest_Expired(unittest.TestCase):
    def setUp(self):
        self.pomo = Pomo()

    def test_expired_default(self):
        self.assertFalse(self.pomo.is_expired(100))

    def test_expired_positive(self):
        self.pomo.start(0.0)
        self.assertTrue(self.pomo.is_expired(25*60+1))

    def test_expired_negative(self):
        self.pomo.start(0.0)
        self.assertFalse(self.pomo.is_expired(25*60-1))

class PomoTest_Cancel(unittest.TestCase):
    def setUp(self):
        self.pomo = Pomo()

    def test_cancel(self):
        self.pomo.start(0)
        self.pomo.cancel()
        self.assertEquals(25*60, self.pomo.get_remaining_time(10))
        self.assertFalse(self.pomo.is_expired(10))
        self.assertTrue(self.pomo.is_paused())

if __name__ == '__main__':
    unittest.main()