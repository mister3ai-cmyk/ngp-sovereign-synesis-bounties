"""
Comprehensive unit and validation tests for SIRT6 epigenetic aging pipeline.
"""

import pytest
import math
from pipeline.pace_pipeline import calculate_pearson_r, run_pace_pipeline

def test_pearson_r_perfect_correlation():
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [2.0, 4.0, 6.0, 8.0, 10.0]
    r = calculate_pearson_r(x, y)
    assert math.isclose(r, 1.0, rel_tol=1e-5)

def test_pearson_r_invalid_lengths():
    with pytest.raises(ValueError):
        calculate_pearson_r([1.0, 2.0], [1.0])

def test_run_pace_pipeline_execution(tmp_path):
    manifest = run_pace_pipeline(output_dir=str(tmp_path))
    assert "dunedinpace" in manifest
    assert math.isclose(manifest["dunedinpace"]["intercept"], 51.024577, abs_tol=0.001)
    assert manifest["correlations"]["H3K9ac_vs_DunedinPACE"]["pearson_r"] > 0.92
    assert manifest["correlations"]["H3K56ac_vs_DunedinPACE"]["pearson_r"] > 0.92
    assert manifest["peak_calling"]["fdr"] < 0.05
    assert manifest["alignment"]["mapq_threshold"] >= 30
    assert manifest["data_deposit_doi"].startswith("10.")
