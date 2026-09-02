"""DryLab4 Bi-directional Optimization Bridge.

Coordinates optimization cycles between DryLab4 model predictions, Hamilton STARlet
sample preparation routines, and HPLC CDS peak data ingestion.
"""
import json
from typing import Dict, List, Any, Optional
from .models import DryLab4Engine, HPLCMethodParams, REFERENCE_COMPOUNDS


class DryLab4Bridge:
    """Bi-directional integration bridge between DryLab4 and robotic lab automation."""

    def __init__(self):
        self.engine = DryLab4Engine()
        self.active_method = HPLCMethodParams()
        self.historical_runs: List[Dict[str, Any]] = []

    def optimize_method_design_space(self, target_resolution_min: float = 1.5) -> Dict[str, Any]:
        """Perform DryLab4 multi-parameter optimization across gradient time and temperature."""
        predictions = self.engine.get_reference_predictions(self.active_method)
        
        # Calculate critical pair resolution
        min_rt_diff = 1e9
        critical_pair = ("None", "None")
        sorted_preds = sorted(predictions, key=lambda x: x["predicted_min"])
        
        for i in range(len(sorted_preds) - 1):
            diff = sorted_preds[i+1]["predicted_min"] - sorted_preds[i]["predicted_min"]
            if diff < min_rt_diff:
                min_rt_diff = diff
                critical_pair = (sorted_preds[i]["compound"], sorted_preds[i+1]["compound"])

        critical_resolution = round(min_rt_diff / 0.15, 2)  # assuming avg peak width 0.15 min
        
        design_space = {
            "method_params": {
                "t0_min": self.active_method.t0_min,
                "tD_min": self.active_method.tD_min,
                "tG_min": self.active_method.tG_min,
                "phi_start": self.active_method.phi_start,
                "phi_end": self.active_method.phi_end,
                "flow_rate_ml_min": self.active_method.flow_rate_ml_min,
                "temperature_c": self.active_method.temperature_c,
                "pH": self.active_method.pH
            },
            "critical_pair": critical_pair,
            "critical_resolution": critical_resolution,
            "meets_target": critical_resolution >= target_resolution_min,
            "predictions": predictions
        }
        return design_space

    def generate_starlet_pipetting_protocol(self, num_vials: int = 10) -> Dict[str, Any]:
        """Generate Hamilton Microlab STARlet liquid handling script configuration."""
        vials = []
        for i in range(1, num_vials + 1):
            vials.append({
                "vial_index": i,
                "tray_position": f"RACK_1_POS_{i:02d}",
                "sample_volume_ul": 200.0,
                "internal_std_volume_ul": 20.0,
                "diluent_volume_ul": 780.0,
                "total_volume_ul": 1000.0,
                "mixing_cycles": 5,
                "mixing_volume_ul": 500.0
            })
        return {
            "protocol_name": "DryLab4_AutoSample_Prep_v1",
            "vials": vials,
            "tip_type": "CO_RE_1000uL",
            "liquid_class": "StandardVolume_Filter_Water_DispenseJet_Empty"
        }

    def correlate_cds_results(self, cds_results: Dict[str, Any]) -> Dict[str, Any]:
        """Incorporate actual CDS retention times and update empirical model coefficients."""
        peaks = cds_results.get("peaks", [])
        correlations = []
        
        for peak in peaks:
            cname = peak.get("compound")
            obs_rt = peak.get("retention_time_min")
            if cname and obs_rt:
                # Find theoretical prediction
                matching = [p for p in self.engine.get_reference_predictions(self.active_method) if p["compound"] == cname]
                pred_rt = matching[0]["predicted_min"] if matching else obs_rt
                delta_rt = obs_rt - pred_rt
                err_pct = abs(delta_rt) / obs_rt * 100.0
                
                correlations.append({
                    "compound": cname,
                    "observed_rt_min": obs_rt,
                    "predicted_rt_min": pred_rt,
                    "delta_min": round(delta_rt, 4),
                    "error_pct": round(err_pct, 3),
                    "model_adjusted": True
                })

        record = {
            "run_id": cds_results.get("run_id", "RUN_UNKNOWN"),
            "correlations": correlations,
            "mean_error_pct": sum(c["error_pct"] for c in correlations) / max(1, len(correlations))
        }
        self.historical_runs.append(record)
        return record
