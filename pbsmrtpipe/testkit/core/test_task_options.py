
from unittest import SkipTest
import logging
import json
import re
import os.path as op
import os

from pbcommand.pb_io.tool_contract_io import load_resolved_tool_contract_from

from pbsmrtpipe.pb_io import parse_pipeline_preset_xml, parse_pipeline_preset_json
from pbsmrtpipe.testkit.core.base import TestValuesLoader
from pbsmrtpipe.models import RunnableTask

log = logging.getLogger(__name__)


class LoadResolvedToolContractMixin(object):

    @classmethod
    def loadRtcs(cls):
        cls.tasks_dir = op.join(cls.job_dir, "tasks")
        task_contents = os.listdir(cls.tasks_dir)
        cls.resolved_tool_contracts = []
        cls.runnable_tasks = []
        for task_name in task_contents:
            task_dir = op.join(cls.tasks_dir, task_name)
            if not op.isdir(task_dir):
                continue
            task_id, job_id = task_name.split("-")
            rtc_json = op.join(task_dir, "resolved-tool-contract.json")
            if not op.isfile(rtc_json):
                log.warn("Can't find %s" % rtc_json)
                continue
            rtc = load_resolved_tool_contract_from(rtc_json)
            cls.resolved_tool_contracts.append(rtc)
            rt_json = op.join(task_dir, "runnable-task.json")
            rt = RunnableTask.from_manifest_json(rt_json)
            cls.runnable_tasks.append(rt)


class TestTaskOptions(TestValuesLoader, LoadResolvedToolContractMixin):
    """
    Validate task options in the resolved tool contracts against a dictionary
    of expected values.
    """

    @classmethod
    def setUpClass(cls):
        super(TestTaskOptions, cls).setUpClass()
        cls.loadRtcs()

    def iterate_rtc_task_options(self):
        for rtc in self.resolved_tool_contracts:
            for key, value in rtc.task.options.iteritems():
                yield key, value

    def test_expected_task_options(self):
        """
        Check task options in RTCs against an explicitly defined list of
        test values.
        """
        if not self.HAVE_TEST_VALUES or not "task_options" in self.test_values:
            raise SkipTest("task_options not defined in test_values.json")
        all_task_options = self.test_values["task_options"]
        n_tested = 0
        for key, value in self.iterate_rtc_task_options():
            task_ns, _, option_id = key.split(".")
            task_options = all_task_options.get(task_ns, {})
            if option_id in task_options:
                self._compare_values(key, value, task_options[option_id])
                n_tested += 1
        if n_tested == 0:
            raise SkipTest("No options tested.")

    def test_runnable_task_options(self):
        n_tested = 0
        for key, value in self.iterate_rtc_task_options():
            for runnable_task in self.runnable_tasks:
                if key in runnable_task.task.resolved_options:
                    n_tested += 1
                    self.assertEqual(runnable_task.task.resolved_options[key], value, "Mismatch between RTC and runnable-task.json for {i}".format(i=key))
        if n_tested == 0:
            raise SkipTest("No options tested.")

    def _compare_values(self, key, observed, expected, as_str=False):
        if expected == None and observed == "":
            return True
        # FIXME this is gross...
        def filter_bool(s): return re.sub("False", "false",
                                          re.sub("True", "true", s))
        if as_str:
            observed, expected = filter_bool(str(observed).strip()), filter_bool(str(expected).strip())
        errmsg = "Failed {k}: {a} != {b}".format(
            k=key, a=observed, b=expected)
        logging.info("Comparing {o} against expected value".format(o=key))
        self.assertEqual(observed, expected, errmsg)

    def test_workflow_task_options_json(self):
        """
        Check task options in RTCs against the options-task.json written by
        pbsmrtpipe.
        """
        json_file = op.join(self.job_dir, "workflow", "options-task.json")
        n_tested = 0
        with open(json_file) as f:
            task_options = json.load(f)
            for key, value in self.iterate_rtc_task_options():
                if key in task_options:
                    self._compare_values(key, value, task_options[key], True)
                    n_tested += 1
        if n_tested == 0:
            raise SkipTest("No options tested.")

    def _load_presets(self):
        preset_xml = op.join(op.dirname(self.job_dir), "preset.xml")
        preset_json = op.join(op.dirname(self.job_dir), "preset.json")
        if not op.isfile(preset_xml) and not op.isfile(preset_json):
            raise SkipTest("No presets JSON or XML found")
        if op.isfile(preset_json):
            return parse_pipeline_preset_json(preset_json)
        elif op.isfile(preset_xml):
            return parse_pipeline_preset_xml(preset_xml)

    def test_preset_task_options(self):
        """
        Check task options in RTCs against the input preset.{xml|json}.
        """
        presets = self._load_presets()
        task_options = dict(presets.task_options)
        if len(task_options) == 0:
            raise SkipTest("presets file uses all default settings")
        n_tested = 0
        for key, value in self.iterate_rtc_task_options():
            if key in task_options:
                self._compare_values(
                    key, value, task_options[key], as_str=True)
                n_tested += 1
        known_options = {k for k,v in self.iterate_rtc_task_options()}
        for key in task_options.keys():
            n_tested += 1
            if not key in known_options:
                self.fail("Task option {k} was not used in this pipeline".format(k=key))
        if n_tested == 0:
            raise SkipTest("No options tested.")

    def test_presets_max_nproc(self):
        """
        Check that nproc for all tasks is no greater than the global setting
        for max_nproc.
        """
        p = self._load_presets()
        max_nproc = dict(p.workflow_options)["pbsmrtpipe.options.max_nproc"]
        n_tested = 0
        for rtc in self.resolved_tool_contracts:
            self.assertTrue(max_nproc >= rtc.task.nproc,
                "Task {i} has nproc > max_nproc ({n} vs {m})".format(
                    i=rtc.task.task_id,
                    n=rtc.task.nproc,
                    m=max_nproc))
            n_tested += 1
        if n_tested == 0:
            raise SkipTest("No options tested.")
