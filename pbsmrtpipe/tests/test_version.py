import unittest
import logging
import platform
import multiprocessing

import pbsmrtpipe

log = logging.getLogger(__name__)


class TestVersion(unittest.TestCase):

    def test_version(self):
        # this is just for logging purposes.
        log.info("Running pbsmrtpipe version {x}".format(x=pbsmrtpipe.get_version()))
        log.info("Running on platform {p}".format(p=platform.platform()))
        log.info("Running on {s}".format(s=platform.node()))
        log.info("Running nproc {n}".format(n=multiprocessing.cpu_count()))
        self.assertIsNotNone(pbsmrtpipe.get_version())
