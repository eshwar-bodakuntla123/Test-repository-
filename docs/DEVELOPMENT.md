# Development

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pip install -e .
pytest
neso-model run emissions_counting --env dev --local
```

Prefer Spark native functions; avoid Python UDFs unless justified. Keep business formulas model-specific.
Add regression tests for every approved formula and never commit credentials/client secrets.
