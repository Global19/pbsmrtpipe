"""Tests for loading ClusterTemplates"""
import os
import logging
import unittest

import pbsmrtpipe.cluster as C

from pbsmrtpipe.cluster import ClusterTemplate, ClusterTemplateRender
from pbsmrtpipe.cluster_templates import CLUSTER_TEMPLATE_DIR


log = logging.getLogger(__name__)


class TestClusterTemplate(unittest.TestCase):

    def test_cluster_template_str(self):
        t = ClusterTemplate('kill', 'qdel ${JOB_ID}')
        self.assertIsNotNone(str(t))
        self.assertIsNotNone(repr(t))

    def test_cluster_template_bad_template_type(self):
        with self.assertRaises(ValueError) as e:
            t = ClusterTemplate('BAD TYPE', 'qdel ${JOB_ID}')
            log.error(e)


class TestCluster(unittest.TestCase):

    def setUp(self):
        self.name = "sge_pacbio"
        self.cluster_model_dir = os.path.join(CLUSTER_TEMPLATE_DIR, self.name)

    def test_basic(self):
        self.assertTrue(os.path.exists(self.cluster_model_dir))

    def test_load_templates(self):
        template_dct = C._get_cluster_files(self.cluster_model_dir)
        self.assertIsNotNone(template_dct)

    def test_load_cluster_templates(self):
        render = C.load_cluster_templates_from_dir(self.cluster_model_dir)

        for cid, cluster_tmpl in render.cluster_templates.iteritems():
            self.assertTrue(isinstance(cluster_tmpl, ClusterTemplate))
            log.info(cluster_tmpl.name)
            log.info(cluster_tmpl.template_str)

    def test_render_cluster_templates(self):
        renderer = C.load_cluster_templates_from_dir(self.cluster_model_dir)
        self.assertIsNotNone(renderer)

        template_name = "interactive"
        command = "python --version"
        job_id = 'c1234'
        nproc = 1

        s = renderer.render(template_name, command, job_id, nproc=nproc)
        self.assertTrue(isinstance(s, basestring))
        log.info("Rendered cluster '{t}'".format(t=template_name))
        log.info(s)


class TestValidateClusterTemplate(unittest.TestCase):

    def _test_validate_template_name_relative_path(self, name):
        p = C.validate_cluster_manager(name)
        self.assertTrue(os.path.isabs(p))

    def test_validate_sge_pacbio_relative_path(self):
        self._test_validate_template_name_relative_path('sge_pacbio')

    def test_validate_pbs_relative_path(self):
        self._test_validate_template_name_relative_path('pbs')

    def test_validate_sge_relative_path(self):
        return self._test_validate_template_name_relative_path('sge')

    def test_validate_load_by_python_module_name(self):
        name = "pbsmrtpipe.cluster_templates.sge"
        cr = C.load_installed_cluster_templates_by_module_name(name)
        self.assertIsInstance(cr, ClusterTemplateRender)
