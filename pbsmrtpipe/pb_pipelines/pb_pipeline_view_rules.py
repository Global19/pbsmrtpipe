#!/usr/bin/env python

"""
Specifies pipeline datastore view rules and generates JSON files for building
into smrtlink.
"""

import argparse
import logging
import os.path as op
import os
import sys

from pbcommand.models import (FileTypes, DataStoreViewRule,
                              PipelineDataStoreViewRules)

log = logging.getLogger(__name__)

REGISTERED_VIEW_RULES = {}


def _to_view_rule(args):
    return DataStoreViewRule(*args)


def load_pipeline_view_rules(registered_views_d, pipeline_id, smrtlink_version,
                             view_rules):
    pvr = PipelineDataStoreViewRules(
        pipeline_id="pbsmrtpipe.pipelines.{p}".format(p=pipeline_id),
        smrtlink_version=smrtlink_version,
        rules=[_to_view_rule(r) for r in view_rules])
    registered_views_d[pipeline_id] = pvr
    return registered_views_d


def register_pipeline_rules(pipeline_id, smrtlink_version):
    def deco_wrapper(func):
        if pipeline_id in REGISTERED_VIEW_RULES:
            log.warn("'{i}' already has view rules defined".format(
                     i=pipeline_id))
        rules = func()
        load_pipeline_view_rules(REGISTERED_VIEW_RULES, pipeline_id,
                                 smrtlink_version, rules)

        def wrapper(*args, **kwds):
            return func(*args, **kwds)
    return deco_wrapper


def _mapping_report_rules():
    return [
        ("pbreports.tasks.mapping_stats-out-0", FileTypes.REPORT, True),
        ("pbreports.tasks.coverage_report-out-0", FileTypes.REPORT, True)
    ]


def _variant_report_rules():
    return [
        ("pbreports.tasks.variants_report-out-0", FileTypes.REPORT, True),
        ("pbreports.tasks.top_variants-out-0", FileTypes.REPORT, True)
    ]

def _basemod_report_rules():
    return [
        ("pbreports.tasks.summarize_coverage-out-0", FileTypes.GFF, True),
        ("kinetics_tools.tasks.summarize_modifications-out-0", FileTypes.GFF, True)
]

def _isoseq_report_rules():
    return [
        ("pbtranscript.tasks.classify-out-3", FileTypes.JSON, True),
        ("pbreports.tasks.isoseq_classify-out-0", FileTypes.REPORT, True)
    ]


def _laa_report_rules():
    return [
        ("pbreports.tasks.amplicon_analysis_input-out-0", FileTypes.REPORT, True),
        ("pbreports.tasks.amplicon_analysis_consensus-out-0", FileTypes.REPORT, True),
        ("pbcoretools.tasks.split_laa_fastq-out-0", FileTypes.GZIP, False, "Consensus Sequences (FASTQ)"),
        ("pbcoretools.tasks.split_laa_fastq-out-1", FileTypes.GZIP, False, "Chimeric/Noise Consensus Sequences (FASTQ)")
    ]


def _barcode_report_rules():
    return [
        ("pbreports.tasks.barcode_report-out-0", FileTypes.REPORT, True)
    ]


def _ccs_report_rules():
    return [
        ("pbreports.tasks.ccs_report-out-0", FileTypes.REPORT, True)
    ]


def _pbalign_alignmentset_rules():
    return [
        ("pbalign.tasks.pbalign-out-0", FileTypes.DS_ALIGN, True)
    ]


@register_pipeline_rules("sa3_ds_barcode", "3.2")
def barcode_view_rules():
    return _barcode_report_rules()


@register_pipeline_rules("sa3_ds_ccs", "3.2")
def ccs_view_rules():
    return _ccs_report_rules()


@register_pipeline_rules("sa3_ds_barcode_ccs", "3.2")
def ccs_barcoding_view_rules():
    return _ccs_report_rules() + _barcode_report_rules()


@register_pipeline_rules("sa3_ds_ccs_align", "3.2")
def ccs_mapping_view_rules():
    return _ccs_report_rules() + _mapping_report_rules() + [
        ("pbreports.tasks.mapping_stats_ccs-out-0", FileTypes.REPORT, True)
    ]


@register_pipeline_rules("ds_modification_detection", "3.2")
def basemod_view_rules():
    return _basemod_report_rules() + _mapping_report_rules() + _pbalign_alignmentset_rules() + [
        ("pbreports.tasks.modifications_report-out-0", FileTypes.REPORT, True)
    ]


@register_pipeline_rules("ds_modification_motif_analysis", "3.2")
def basemod_and_motif_view_rules():
    return _basemod_report_rules() + _mapping_report_rules() + _pbalign_alignmentset_rules() + [
        ("pbreports.tasks.modifications_report-out-0", FileTypes.REPORT, True),
        ("pbreports.tasks.motifs_report-out-0", FileTypes.REPORT, True),
        ("kinetics_tools.tasks.ipd_summary-out-0", FileTypes.GFF, True)
    ]


@register_pipeline_rules("polished_falcon_fat", "3.2")
def hgap4_view_rules():
    return [
        ("pbcoretools.tasks.bam2fasta-out-0", FileTypes.FASTA , True),
        ("pbcoretools.tasks.fasta2fofn-out-0", FileTypes.FOFN , True),
        ("pbcoretools.tasks.contigset2fasta-out-0", FileTypes.FASTA, False, "Polished Assembly"),
        ("falcon_ns.tasks.task_falcon_make_fofn_abs-out-0", FileTypes.FOFN , True),
        ("falcon_ns.tasks.task_falcon0_build_rdb-out-0", FileTypes.TXT , True),
        ("falcon_ns.tasks.task_falcon0_build_rdb-out-1", FileTypes.TXT,True),
        ("genomic_consensus.tasks.variantcaller-out-0", FileTypes.GFF,True),
        ("genomic_consensus.tasks.variantcaller-out-1", FileTypes.DS_CONTIG, False, "Polished Assembly"),
        ("genomic_consensus.tasks.variantcaller-out-2", FileTypes.FASTQ, False, "Polished Assembly"),
        ("genomic_consensus.tasks.gff2vcf-out-0", FileTypes.VCF,True),
        ("genomic_consensus.tasks.gff2bed-out-0", FileTypes.BED,True),
        ("falcon_ns.tasks.task_falcon1_build_pdb-out-0", FileTypes.TXT , True),
        ("falcon_ns.tasks.task_falcon0_run_daligner_jobs-out-0", FileTypes.FOFN , True),
        ("falcon_ns.tasks.task_falcon0_run_merge_consensus_jobs-out-0", FileTypes.FOFN , True),
        ("falcon_ns.tasks.task_falcon0_run_merge_consensus_jobs-out-1", FileTypes.JSON , False),
        ("falcon_ns.tasks.task_falcon0_run_merge_consensus_jobs-out-2", FileTypes.JSON , False),
        ("falcon_ns.tasks.task_falcon0_merge-out-0", FileTypes.TXT , False),
        ("falcon_ns.tasks.task_falcon0_cons-out-0", FileTypes.TXT , False),
        ("falcon_ns.tasks.task_falcon1_run_daligner_jobs-out-0", FileTypes.FOFN , True),
        ("falcon_ns.tasks.task_falcon1_run_merge_consensus_jobs-out-0", FileTypes.FOFN , True),
        ("falcon_ns.tasks.task_falcon1_run_merge_consensus_jobs-out-1", FileTypes.JSON , False),
        ("falcon_ns.tasks.task_falcon1_run_merge_consensus_jobs-out-2", FileTypes.JSON , False),
        ("falcon_ns.tasks.task_falcon1_merge-out-0", FileTypes.TXT , False),
        ("falcon_ns.tasks.task_falcon1_db2falcon-out-0", FileTypes.TXT , False),
        ("falcon_ns.tasks.task_falcon2_run_asm-out-0", FileTypes.FASTA, True),
        ("falcon_ns.tasks.task_falcon_gen_config-out-0", FileTypes.CFG , True),
        ("falcon_ns.tasks.task_falcon0_build_rdb-out-2", FileTypes.TXT , True),
        ("falcon_ns.tasks.task_falcon_config-out-0", FileTypes.JSON, True),
        ("pbreports.tasks.polished_assembly-out-0", FileTypes.REPORT , True),
        ("falcon_ns.tasks.task_report_preassembly_yield-out-0", FileTypes.REPORT , True),
        ("pbcoretools.tasks.fasta2referenceset-out-0", FileTypes.DS_REF, False, "Draft Assembly")
    ] + _mapping_report_rules()


@register_pipeline_rules("hgap_fat", "3.2")
def hgap5_view_rules():
    return [
        ("falcon_ns.tasks.task_hgap_prepare-out-0", FileTypes.JSON, True),
        ("falcon_ns.tasks.task_hgap_prepare-out-1", FileTypes.JSON, True),
        ("falcon_ns.tasks.task_hgap_prepare-out-2", FileTypes.LOG, True),
        ("falcon_ns.tasks.task_hgap_run-out-1", FileTypes.REPORT, True),
        ("falcon_ns.tasks.task_hgap_run-out-2", FileTypes.REPORT, True),
        ("falcon_ns.tasks.task_hgap_run-out-3", FileTypes.LOG, True)
    ]


@register_pipeline_rules("sa3_ds_isoseq", "3.2")
def isoseq_view_rules():
    return _isoseq_report_rules() + _ccs_report_rules() + [
        ("pbtranscript.tasks.separate_flnc-out-0", FileTypes.PICKLE, True),
        ("pbtranscript.tasks.create_chunks-out-0", FileTypes.PICKLE, True),
        ("pbtranscript.tasks.create_chunks-out-1", FileTypes.PICKLE, True),
        ("pbtranscript.tasks.create_chunks-out-2", FileTypes.PICKLE, True),
        ("pbtranscript.tasks.combine_cluster_bins-out-7", FileTypes.PICKLE, True),
        ("pbtranscript.tasks.gather_ice_partial_cluster_bins_pickle-out-0",
         FileTypes.TXT, True),
        ("pbtranscript.tasks.cluster_bins-out-0", FileTypes.TXT, True),
        ("pbtranscript.tasks.ice_partial_cluster_bins-out-0", FileTypes.TXT, True),
        ("pbtranscript.tasks.ice_polish_cluster_bins-out-0", FileTypes.TXT, True),
        ("pbtranscript.tasks.gather_polished_isoforms_in_each_bin-out-0",
         FileTypes.TXT, True),
        ("pbtranscript.tasks.ice_cleanup-out-0", FileTypes.TXT, True),
        ("pbtranscript.tasks.combine_cluster_bins-out-1", FileTypes.JSON, True),
        ("pbreports.tasks.isoseq_cluster-out-0", FileTypes.REPORT, True)

    ]


@register_pipeline_rules("sa3_ds_isoseq_classify", "3.2")
def isoseq_classify_view_rules():
    return _isoseq_report_rules() + _ccs_report_rules()


@register_pipeline_rules("sa3_ds_laa", "3.2")
def laa_view_rules():
    r1 = [
        ("pblaa.tasks.laa-out-3", FileTypes.CSV, True)
    ]
    return r1 + _laa_report_rules()


@register_pipeline_rules("sa3_ds_barcode_laa", "3.2")
def laa_barcode_view_rules():
    r1 = [("pblaa.tasks.laa-out-3", FileTypes.CSV, True)]
    return _barcode_report_rules() + r1 + _laa_report_rules()


@register_pipeline_rules("sa3_sat", "3.2")
def sat_view_rules():
    return _pbalign_alignmentset_rules() + _mapping_report_rules() + _variant_report_rules() + [
        ("pbreports.tasks.sat_report-out-0", FileTypes.REPORT, True)
    ]


@register_pipeline_rules("sa3_ds_resequencing_fat", "3.2")
def resequencing_view_rules():
    return _pbalign_alignmentset_rules() + _mapping_report_rules() + _variant_report_rules() + [
        ("genomic_consensus.tasks.variantcaller-out-1", FileTypes.DS_CONTIG, False, "Consensus Sequences"),
        ("genomic_consensus.tasks.variantcaller-out-2", FileTypes.FASTQ, False, "Consensus Sequences")
]

def main(argv):
    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", action="store", default=os.getcwd(),
                   help="Output directory for JSON files")
    args = p.parse_args(argv[1:])
    for pipeline_id, rules in REGISTERED_VIEW_RULES.iteritems():
        file_name = op.join(args.output_dir, "pipeline_datastore_view_rules-{p}.json".format(p=pipeline_id))
        log.info("Writing {f}".format(f=file_name))
        rules.write_json(file_name)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
