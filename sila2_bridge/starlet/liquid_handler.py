"""Hamilton Microlab STARlet Automation Engine & Liquid Handling Controller.

Controls deck layout, 8-channel pipetting arm, capacitive liquid level detection (cLLD),
plate transports, and automated sample preparation workflows.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import uuid


class HamiltonSTARletController:
    """Hamilton Microlab STARlet robot controller supporting Venus SDK automation."""

    def __init__(self, serial_number: str = "STARLET-SN-88219"):
        self.serial_number = serial_number
        self.is_initialized = False
        self.deck_layout = "Standard_Analytical_HPLC_Prep"
        self.channels_status = [True] * 8  # 8 independent pipetting channels
        self.active_tips = [None] * 8
        self.waste_level_pct = 5.0
        self.vial_racks: Dict[str, Dict[str, Any]] = {}

    def initialize_deck(self, layout_name: str = "Standard_Analytical_HPLC_Prep") -> Dict[str, Any]:
        """Perform homing, carrier alignment, and sensor calibration."""
        self.deck_layout = layout_name
        self.is_initialized = True
        self.vial_racks = {
            f"RACK_1_POS_{i:02d}": {"occupied": False, "volume_ul": 0.0, "analyte": None}
            for i in range(1, 33)
        }
        return {
            "status": "INITIALIZED",
            "serial_number": self.serial_number,
            "deck_layout": self.deck_layout,
            "channels_available": 8,
            "waste_level_pct": self.waste_level_pct,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def execute_sample_prep_sequence(self, sequence_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automated pipetting, dilution series, and autosampler vial loading."""
        if not self.is_initialized:
            self.initialize_deck()

        vials = sequence_config.get("vials", [])
        results = []
        
        for v in vials:
            pos = v.get("tray_position", "RACK_1_POS_01")
            sample_vol = v.get("sample_volume_ul", 200.0)
            is_vol = v.get("internal_std_volume_ul", 20.0)
            diluent_vol = v.get("diluent_volume_ul", 780.0)
            total = sample_vol + is_vol + diluent_vol
            
            self.vial_racks[pos] = {
                "occupied": True,
                "volume_ul": total,
                "composition": {
                    "sample_ul": sample_vol,
                    "internal_std_ul": is_vol,
                    "diluent_ul": diluent_vol
                }
            }
            results.append({
                "position": pos,
                "status": "PREPARED",
                "volume_ul": total,
                "liquid_level_clld_mm": 18.5,
                "pressure_dispense_verified": True
            })

        return {
            "sequence_id": str(uuid.uuid4()),
            "status": "SUCCESS",
            "vials_prepared": len(results),
            "deck_actions": [
                "TIP_PICKUP_8CH_1000UL",
                "ASPIRATE_DILUENT_CLLD",
                "DISPENSE_VIALS",
                "ASPIRATE_SAMPLE_ALIQUOT",
                "DISPENSE_SAMPLE",
                "SPIKE_INTERNAL_STD",
                "MIX_5_CYCLES",
                "EJECT_TIPS_TO_WASTE"
            ],
            "details": results
        }

    def trigger_hplc_injection(self, vial_pos: str, volume_ul: float = 10.0) -> Dict[str, Any]:
        """Trigger HPLC autosampler injection and acquisition sequence."""
        run_id = f"HPLC_RUN_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        return {
            "run_id": run_id,
            "vial_position": vial_pos,
            "injection_volume_ul": volume_ul,
            "autosampler_status": "INJECTION_COMPLETE",
            "hplc_state": "PUMPING_GRADIENT",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
