import unittest
import logging

from base import was_backticks_successful

log = logging.getLogger(__name__)

_PBTOOLS_EXE = ("pbsmrtpipe", "pbtools-runner")


class TestExternalToolsSanity(unittest.TestCase):

    def test_help(self):
        """
        Crude cram-esque test test if installed pbsmrtpipe exe's are
        working"""
        for exe in _PBTOOLS_EXE:
            cmd = "{e} --help".format(e=exe)
            was_successful = was_backticks_successful(cmd)
            emsg = "Command '{e}' was not successful".format(e=cmd)
            self.assertTrue(was_successful, emsg)
