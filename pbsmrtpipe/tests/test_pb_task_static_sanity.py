import unittest
import logging

log = logging.getLogger(__name__)


class TestSanity(unittest.TestCase):

    def test_load_static_tasks(self):
        import pbsmrtpipe.loader as L
        static_meta_tasks = L.load_all_pb_tool_contracts()
        log.debug("Static Meta Tasks")
        log.debug(static_meta_tasks)
        self.assertIsNotNone(static_meta_tasks)
        self.assertTrue(len(static_meta_tasks) > 0)
