import unittest

class Storage:
    def __init__(self):
        None

class StorageTest(unittest.TestCase):
    def setUp(self):
        None

    def test_load_invalid_datastore(self):
        None

    def test_load(self):
        # Configure file double to have contents of some tasks
        self.storage = Storage()
        self.assertTrue(self.storage.load('test_file'))
        # Check that all tasks are loaded successfully

if __name__ == '__main__':
    unittest.main()