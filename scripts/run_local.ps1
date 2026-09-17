$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    py -3.11 -m venv .venv
}

. .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .

ruff check framework models tests api
ruff format --check framework models tests api
pytest --cov=framework --cov=models --cov-fail-under=80

neso-model run emissions_counting --env dev --local
