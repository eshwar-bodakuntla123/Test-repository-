# Development

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pip install -e .

ruff check framework models tests api
ruff format --check framework models tests api
pytest --cov=framework --cov=models --cov-fail-under=80

neso-model run emissions_counting --env dev --local
```

## Coding rules

- Prefer Spark native expressions.
- Avoid Python UDFs unless justified.
- Keep formulas in model-specific packages.
- Keep reusable mechanics in `framework/`.
- Add tests for all shared functionality.
- Add regression tests for every SME-approved business formula.
- Do not commit credentials or client data to a personal/public repository.
