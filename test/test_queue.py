import greenstalk
import unittest


class TestQueue(unittest.TestCase):
    default_queue = greenstalk.Client(host='127.0.0.1', port=12000)
    custom_queue = greenstalk.Client(host='127.0.0.1', port=12000, use="custom")

    def testDefaultQueue(self):
        self.default_queue.put("hello")
        job = self.default_queue.reserve(timeout=5)
        self.assertEqual("hello", job.body)
        self.default_queue.delete(job)

        try:
            self.default_queue.reserve(timeout=5)
            self.assertTrue(False)
        except greenstalk.TimedOutError:
            pass

    def testCustomQueue(self):
        self.custom_queue.put("hello")
        job = self.custom_queue.reserve(timeout=5)
        self.assertEqual("hello", job.body)
        self.custom_queue.delete(job)

        try:
            self.custom_queue.reserve(timeout=5)
            self.assertTrue(False)
        except greenstalk.TimedOutError:
            pass
