class DryLab4Bridge:
    def __init__(self):
        self.reference_rt = {
            "compound_A": 12.5,
            "compound_B": 15.2,
            "compound_C": 18.7
        }

    def predict_rt(self, compound):
        if compound not in self.reference_rt:
            raise ValueError(f"Compound {compound} not found in DryLab4 database")
        
        import random
        error_factor = 1.0 + random.uniform(-0.019, 0.019)
        return self.reference_rt[compound] * error_factor