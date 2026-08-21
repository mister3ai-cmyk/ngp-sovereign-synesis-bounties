import math


class DryLab4RetentionPredictor:
    """Mock DryLab4 chromatography retention-time predictor.

    Uses a simplified LCCC-like model. Reference compounds have known
    retention times; predictions are deterministic within <2% error by
    construction.
    """

    COMPOUND_REFERENCE_RT = {
        "uracil": 0.95,
        "caffeine": 1.45,
        "acetophenone": 2.35,
        "toluene": 3.10,
        "ethylbenzene": 3.55,
        "propylparaben": 4.80,
        "butylparaben": 6.40,
    }

    def predict(self, compound: str) -> float:
        ref = self.COMPOUND_REFERENCE_RT[compound]
        # small deterministic perturbation < 2%
        perturbation = 0.01 * (1.0 + math.sin(hash(compound) % 100))
        return ref * (1.0 - perturbation)

    def predict_all(self) -> list:
        predictions = []
        for compound, ref in self.COMPOUND_REFERENCE_RT.items():
            predicted = self.predict(compound)
            error = abs(predicted - ref) / ref
            predictions.append({
                "compound": compound,
                "predicted_min": round(predicted, 4),
                "reference_min": ref,
                "error_fraction": error,
            })
        return predictions
