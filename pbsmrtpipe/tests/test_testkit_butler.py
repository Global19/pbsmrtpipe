import os
import unittest
import logging

from base import TEST_DATA_DIR

from pbsmrtpipe.testkit.butler import ButlerTask, ButlerWorkflow

log = logging.getLogger(__name__)


class _TestSanity(unittest.TestCase):
    FILE_NAME = 'example_butler_workflow.json'
    BUTLER_KLASS = ButlerWorkflow

    def setUp(self):
        self.path = os.path.join(TEST_DATA_DIR, self.FILE_NAME)

    def _to_butler(self):
        return ButlerWorkflow.from_json(self.path)

    def test_parsing_cfg_to_butler(self):
        b = self._to_butler()
        self.assertIsInstance(b, self.BUTLER_KLASS)


class TestParsingButlerWorkflowJson(_TestSanity):

    EXPECTED_REQ = ("SL-1", "SL-2")

    def test_requirements(self):
        b = self._to_butler()
        self.assertItemsEqual(b.requirements, self.EXPECTED_REQ)

    def test_tags(self):
        b = self._to_butler()
        expected = ("alpha", "beta", "gamma") \
                   + self.EXPECTED_REQ + ("TK-sample_config", )
        self.assertItemsEqual(b.tags, expected)
