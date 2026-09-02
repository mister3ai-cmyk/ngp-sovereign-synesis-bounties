process RUN_PACE_PIPELINE {
    tag "pace_pipeline"
    publishDir "results", mode: 'copy'

    output:
    path "manifest.json"

    script:
    """
    python3 ${baseDir}/pipeline/pace_pipeline.py
    """
}

workflow {
    RUN_PACE_PIPELINE()
}
