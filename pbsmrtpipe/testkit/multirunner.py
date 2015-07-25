import time
import operator
import multiprocessing
import logging
import sys
import os

from pbcommand.cli import pacbio_args_runner, get_default_argparser
from pbcommand.utils import setup_log

import pbsmrtpipe.tools.utils as TU
from pbsmrtpipe.utils import validate_file, compose
from pbsmrtpipe.engine import backticks

__version__ = '0.1.0'


log = logging.getLogger(__name__)

_EXE = 'pbtestkit-runner'


def _testkit_cfg_fofn_to_files(butler_fofn, root_dir):
    """
    Parse the butler FOFN and return a list of butler cfgs with absolute path.

    :param butler_fofn: (str) path to butler fofn.
    :param root_dir: (str) root dir that butler.fofn are relative to.
    """
    testkit_cfgs = []
    with open(butler_fofn, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                log.debug("Skipping {l}".format(l=line))
            else:
                p = os.path.join(root_dir, line)
                if os.path.exists(p):
                    if p not in testkit_cfgs:
                        testkit_cfgs.append(p)
                else:
                    # Don't want the tests to not run if there's an error here
                    msg = "Unable to find {f} from butler fofn {x}".format(f=p, x=butler_fofn)
                    sys.stderr.write(msg + "\n")
                    log.error(msg)

    log.info("Parsed file {f}. Found {n} configs.".format(f=butler_fofn, n=len(testkit_cfgs)))
    for c in testkit_cfgs:
        log.info(c)

    return testkit_cfgs


def testkit_cfg_fofn_to_files(fofn):
    return _testkit_cfg_fofn_to_files(fofn, os.path.dirname(fofn))


def _validate_testkit_cfg_fofn(path):
    p = os.path.abspath(path)
    # files will be relative the supplied fofn
    dir_name = os.path.dirname(p)
    _testkit_cfg_fofn_to_files(p, dir_name)
    return p

validate_testkit_cfg_fofn = compose(_validate_testkit_cfg_fofn, validate_file)


def _run_testkit_cfg(testkit_cfg, debug=False):
    os.chdir(os.path.dirname(testkit_cfg))
    cmd = "{e} --debug {c}".format(c=testkit_cfg, e=_EXE)
    rcode, stdout, stderr, run_time = backticks(cmd)

    if debug:
        log.debug(" ".join([str(i) for i in [cmd, rcode, stdout, stderr]]))

    # Returning the butler cfg is a bit odd, but this is necessary for the
    # parallelism to work consistently with the serial version
    return testkit_cfg, rcode, stdout, stderr, run_time


def run_testkit_cfgs(testkit_cfgs, nworkers):
    """Run all the butler cfgs in parallel or serial (nworkers=1)

    :param testkit_cfgs: (list of str) list of absolute paths to butler.cfgs)
    :param nworkers: (int) Number of workers to spawn.

    :type testkit_cfgs: list
    :type nworkers: int

    :rtype: bool
    """
    started_at = time.time()
    log.info("Starting with nworkers {n} and {m} butler cfg files".format(n=nworkers, m=len(testkit_cfgs)))
    results = []
    if nworkers == 1:
        log.info("Running in serial mode.")
        for testkit_cfg in testkit_cfgs:
            bcfg, rcode, stdout, stderr, job_run_time = _run_testkit_cfg(testkit_cfg)
            d = dict(x=testkit_cfg, r=rcode, s=int(job_run_time), m=job_run_time / 60.0)
            log.info("Completed running {x}. exit code {r} in {s} sec ({m:.2f} min).".format(**d))
            results.append((testkit_cfg, rcode, stdout, stderr, job_run_time))
    else:
        pool = multiprocessing.Pool(nworkers)
        results = pool.map_async(_run_testkit_cfg, testkit_cfgs).get(9999999)

    log.info("Results:")
    for bcfg, rcode, _, _, job_run_time in results:
        d = dict(r=rcode, j=bcfg, s=int(job_run_time), m=job_run_time / 60.0)
        log.info("exit code {r} in {s} sec ({m:.2f} min). job {j}".format(**d))

    njobs = len(results)
    rcodes = [operator.getitem(r, 1) for r in results]
    nfailed = len([r for r in rcodes if r != 0])
    run_time = time.time() - started_at

    d = dict(n=njobs, x=nfailed, s=int(run_time), m=run_time / 60.0)
    msg = "Completed {n} jobs in {s} sec ({m:.2f} min) {x} failed.".format(**d)
    print msg
    log.info(msg)

    # should this propagate the rcodes from siv_butler calls?
    return 0 if nfailed == 0 else -1


def _args_run_multi_testkit_cfg(args):

    testkit_cfgs = testkit_cfg_fofn_to_files(args.testkit_cfg_fofn)

    nworkers = min(len(testkit_cfgs), args.nworkers)

    return run_testkit_cfgs(testkit_cfgs, nworkers)


def get_parser():
    desc = "Run multiple testkit.cfg files in parallel"
    p = get_default_argparser(__version__, desc)
    TU.add_debug_option(p)
    TU.add_force_distribute_option(p)

    p.add_argument('testkit_cfg_fofn', type=validate_testkit_cfg_fofn,
                   help="File of butler.cfg file name relative to the current dir (e.g., RS_Resquencing/testkit.cfg")
    p.add_argument('-n', '--nworkers', type=int, default=1, help="Number of jobs to concurrently run.")

    p.set_defaults(func=_args_run_multi_testkit_cfg)
    return p


def main(argv=None):

    argv_ = sys.argv if argv is None else argv
    parser = get_parser()
    return pacbio_args_runner(argv_[1:], parser, _args_run_multi_testkit_cfg, log, setup_log)
