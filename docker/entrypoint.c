/*
 * Minimal static entrypoint for the NGP Sovereign Synesis Bounty #1
 * pipeline image. Prints pipeline provenance and the image digest.
 * The production image replaces this with the full bwa/samtools/MACS3
 * environment defined in Dockerfile (see Dockerfile.prod).
 */
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    (void)argc; (void)argv;
    printf("ngp-sovereign-synesis-bounties | Bounty #1 ChIP-seq & DunedinPACE pipeline\n");
    printf("image: ngp-pace-pipeline:latest\n");
    printf("pipeline: Snakemake | align(MAPQ>=30) -> peaks(FDR<0.05) -> DunedinPACE -> correlation\n");
    printf("content: /opt/ngp-pace-pipeline/{Snakefile,config,scripts,data}\n");
    return 0;
}