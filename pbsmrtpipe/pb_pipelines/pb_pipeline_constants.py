import functools

from pbcommand.models import FileTypes

from pbsmrtpipe.constants import ENTRY_PREFIX

def _to_entry(entry_prefix, value):
    return "".join([entry_prefix, value])

to_entry = functools.partial(_to_entry, ENTRY_PREFIX)


class Constants(object):

    ENTRY_RS_MOVIE_XML = to_entry("rs_movie_xml")
    ENTRY_INPUT_XML = to_entry("eid_input_xml")
    ENTRY_REF_FASTA = to_entry("eid_ref_fasta")

    ENTRY_DS_REF = to_entry("eid_ref_dataset")
    ENTRY_DS_BARCODE = to_entry("eid_barcode")
    ENTRY_BAM_ALIGNMENT = to_entry("eid_bam_alignment")
    ENTRY_DS_HDF = to_entry("eid_hdfsubread")
    ENTRY_DS_SUBREAD = to_entry("eid_subread")
    ENTRY_DS_ALIGN = to_entry("eid_alignment")
    ENTRY_DS_CCS = to_entry("eid_ccs")
    ENTRY_DS_GMAPREF = to_entry("eid_gmapref_dataset")
    ENTRY_DS_TRANSCRIPT = to_entry("eid_transcript")

    # This should only be used for internal use
    ENTRY_COND_JSON = to_entry("cond_json")

    ENTRY_FILE_TYPES = {
        ENTRY_RS_MOVIE_XML: FileTypes.RS_MOVIE_XML,
        ENTRY_INPUT_XML: FileTypes.INPUT_XML,
        ENTRY_REF_FASTA: FileTypes.FASTA,
        ENTRY_DS_REF: FileTypes.DS_REF,
        ENTRY_DS_BARCODE: FileTypes.DS_BARCODE,
        ENTRY_BAM_ALIGNMENT: FileTypes.BAM,
        ENTRY_DS_HDF: FileTypes.DS_SUBREADS_H5,
        ENTRY_DS_SUBREAD: FileTypes.DS_SUBREADS,
        ENTRY_DS_ALIGN: FileTypes.DS_ALIGN,
        ENTRY_DS_CCS: FileTypes.DS_CCS,
        ENTRY_DS_GMAPREF: FileTypes.DS_GMAP_REF,
        ENTRY_COND_JSON: FileTypes.COND_RESEQ
    }


class Tags(object):
    # General Analysis Categories
    MAP = "mapping"
    CONSENSUS = "consensus"
    RPT = "reports"
    CCS = "ccs"
    LAA = "laa"
    MOD_DET = "modification-detection"
    MOTIF = "motif-analysis"
    ISOSEQ = "isoseq"
    DENOVO = "denovo"
    SAT = "sat"
    MINORVAR = "minorvariants"
    SV = "sv"

    BARCODE = "barcode"

    # File format converters
    CONVERTER = "converters"

    # These pipelines will NOT show up in the UI
    # Development/Diagnostic
    DEV = "dev"
    # Internal Analysis
    INTERNAL = "internal"
    # Mulit-analysis jobs
    COND = "conditions"
    # Beta pipelines
    BETA = "beta"
    ALPHA = "alpha"

    RESEQ = (MAP, CONSENSUS)
    RESEQ_INTERNAL = (MAP, CONSENSUS, INTERNAL)
    RESEQ_RPT = (MAP, CONSENSUS, RPT)
    RESEQ_MOD_DET = (MAP, CONSENSUS, MOD_DET)
    RESEQ_MOTIF = (MAP, CONSENSUS, MOD_DET, MOTIF)
