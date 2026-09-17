class FormulaRegistry:
    def __init__(self): self._rules={}
    def register(self, formula_id):
        def deco(fn):
            if formula_id in self._rules: raise ValueError(f"Formula already registered: {formula_id}")
            self._rules[formula_id]=fn; return fn
        return deco
    def get(self, formula_id): return self._rules[formula_id]
    def list(self): return sorted(self._rules)
FORMULAS=FormulaRegistry()
