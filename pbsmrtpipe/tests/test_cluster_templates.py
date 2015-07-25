import unittest
import logging
import pprint

log = logging.getLogger(__name__)

from base import HAS_CLUSTER_QSUB, TestDirBase
import pbsmrtpipe.cluster as C


class TestInstalledClusterTemplates(unittest.TestCase):

    def test_sanity(self):
        cluster_renders = C.load_installed_cluster_templates()
        log.debug(pprint.pformat(cluster_renders))
        self.assertIsNotNone(cluster_renders)


@unittest.skipIf(not HAS_CLUSTER_QSUB, "Cluster is not accessible")
class TestHelloClusterWorld(TestDirBase):

    def test_hello(self):
        self.assertTrue(True)
