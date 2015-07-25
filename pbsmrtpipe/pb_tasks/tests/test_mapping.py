import logging

from pbsmrtpipe.models import TaskTypes
import pbsmrtpipe.schema_opt_utils as OP

from task_test_base import _TaskTestBase

log = logging.getLogger(__name__)


class TestFastaReferenceToReport(_TaskTestBase):
    TASK_ID = 'pbsmrtpipe.tasks.ref_to_report'
    INPUT_FILE_NAMES = ['reference.fasta']

    RESOLVED_TASK_TYPE = TaskTypes.LOCAL


class TestAlignTaskDefaultOptions(_TaskTestBase):
    TASK_ID = "pbsmrtpipe.tasks.align"
    INPUT_FILE_NAMES = "movie.fofn region.fofn reference.fasta reference_info_report.json".split()
    MAX_NPROC = 24

    NCOMMANDS = 5
    RESOLVED_NPROC = 24
    RESOLVED_TASK_OPTIONS = {"pbsmrtpipe.task_options.load_pulses": True}


class TestAlignTaskCustomOptions(TestAlignTaskDefaultOptions):
    TASK_OPTIONS = {OP.to_opt_id('max_hits'): 1,
                    OP.to_opt_id('max_error'): 30,
                    OP.to_opt_id('min_anchor_size'): 12,
                    OP.to_opt_id('pbalign_opts'): ' --minAccuracy=0.75 --minLength=50 '}


class TestAlignBamDefaults(_TaskTestBase):
    TASK_ID = "pbsmrtpipe.tasks.bam_align"
    INPUT_FILE_NAMES = ["movie.fofn", "rgn.fofn", "reference.fasta", "reference_report.json"]
    TASK_OPTIONS = {}
    MAX_NPROC = 7

    NCOMMANDS = 1
    RESOLVED_TASK_OPTIONS = {}
    RESOLVED_NPROC = 7


class TestAlignBamCustom(TestAlignBamDefaults):
    pass
