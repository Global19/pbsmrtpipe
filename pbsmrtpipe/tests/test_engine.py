import logging
import os
import unittest
import time
import tempfile
import stat
import multiprocessing
import warnings

from pbsmrtpipe.engine import (ProcessPoolManager, EngineWorker,
                               get_results_from_queue, backticks)
from pbsmrtpipe.cluster_templates import CLUSTER_TEMPLATE_DIR
from pbsmrtpipe.cluster import ClusterTemplateRender

from base import HAS_CLUSTER_QSUB, NO_CLUSTER_COMMAND_MESSAGE

log = logging.getLogger(__name__)


class TestUtilFuncs(unittest.TestCase):

    def test_backticks(self):

        exe = 'python --version'

        rcode, out, err, run_time = backticks(exe)

        self.assertEqual(rcode, 0)

        self.assertTrue(out[0].startswith('Python '))

        self.assertEqual(err, "")


def _task_generator(max_tasks):
    def _to_tmp(suffix):
        t = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        t.close()
        return t.name

    tasks = []
    for i in xrange(max_tasks):
        task_url = 'task://{i}/task_0{i}'.format(i=i)
        task_job_id = "j0{i}".format(i=i)

        cmd = "echo \"Task {i}\"; sleep 2".format(i=i)
        script_path = _to_tmp("_task_{i}.sh".format(i=i))
        with open(script_path, 'w+') as f:
            f.write(cmd)
        permissions = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH
        os.chmod(script_path, permissions)

        stderr = _to_tmp("_{i}_stderr".format(i=i))
        stdout = _to_tmp("_{i}_stdout".format(i=i))
        nproc = 1
        d = (task_job_id, script_path, stdout, stderr, nproc)
        log.info("Added to in_q {d}".format(d=d))
        tasks.append(d)

    return tasks


def _test_engine_worker_basic():
    m = multiprocessing.Manager()
    shutdown_event = m.Event()
    out_q = m.Queue()
    sleep_time = 1

    tasks = _task_generator(1)
    task_job_id, script, stdout, stderr, nproc = tasks[0]

    w = EngineWorker(out_q, shutdown_event, task_job_id, script, stdout, stderr, nproc, sleep_time=sleep_time)

    w.start()

    time.sleep(5)

    print "Process {i} is alive? {a}".format(i=w.pid, a=w.is_alive())
    w.shutdown_event.set()

    results = get_results_from_queue(out_q)
    print results
    return results


def _test_pool(max_workers, tasks, cluster_renderer=None):
    """

    Each task must have the form (task-id,

    :param max_workers:
    :param tasks:
    :param cluster_renderer:
    :return:
    """
    log.debug("Testing processing pool with max worker:{m} max tasks:{t} cluster render {c}".format(m=max_workers, t=len(tasks), c=cluster_renderer))

    max_tasks = len(tasks)

    m = multiprocessing.Manager()
    # pool shutdown
    shutdown_event = m.Event()
    # worker shutdown
    worker_shutdown_event = m.Event()
    out_q = m.Queue()
    in_q = m.Queue()
    sleep_time = 1

    for task in tasks:
        log.info("Adding task {t} to queue".format(t=task))
        in_q.put(task)

    job_id = 'j1234'
    p = ProcessPoolManager(job_id, worker_shutdown_event, shutdown_event, in_q, out_q, max_workers, sleep_time=sleep_time, cluster_renderer=cluster_renderer)

    p.start()

    results = []
    while len(results) < max_tasks:
        rs = get_results_from_queue(out_q)
        for r in rs:
            print r
            results.append(r)
        time.sleep(1)

    log.info("Settings Pool shutdown event.")
    p.shutdown_event.set()

    wait_time = 10
    log.info("waiting/sleeping for {s} sec.".format(s=wait_time))
    time.sleep(wait_time)

    print "in q size ", in_q.qsize()
    print "outq size ", out_q.qsize()

    # this blocks untill in in_q is empty
    # p.join(timeout=5)
    p.terminate()

    return results


def _test_simple_pool(max_workers, max_tasks, cluster_renderer=None):
    tasks = _task_generator(max_tasks)
    return _test_pool(max_workers, tasks, cluster_renderer=cluster_renderer)


@unittest.skip
class TestWorker(unittest.TestCase):

    def test_basic(self):
        results = _test_engine_worker_basic()
        self.assertTrue(len(results), 1)


@unittest.skip
class TestProcessPoolManager(unittest.TestCase):

    def test_basic(self):
        max_tasks = 10
        max_workers = 3
        results = _test_simple_pool(max_workers, max_tasks)
        self.assertEqual(len(results), max_tasks)


@unittest.skipIf(not HAS_CLUSTER_QSUB, NO_CLUSTER_COMMAND_MESSAGE)
class TestClusterProcessPoolManager(unittest.TestCase):

    def test_cluster_pool(self):
        name = 'sge'
        template_dir = os.path.join(CLUSTER_TEMPLATE_DIR, name)

        # Extra checking to make sure tests don't fail because of
        # configuration of the system.
        if os.path.exists(template_dir):
            cluster_renderer = ClusterTemplateRender.from_dir(template_dir)
            max_tasks = 5
            max_workers = 3
            results = _test_simple_pool(max_workers, max_tasks, cluster_renderer=cluster_renderer)
            self.assertEqual(len(results), max_tasks)
        else:
            msg = "Manually skipping {k}. Unable to cluster template '{t}'".format(k=self.__class__.__name__, t=template_dir)
            warnings.warn(msg)
            log.warn(msg)

        self.assertTrue(True)
