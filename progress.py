neso-model-platform/
│
├── src/
│   └── neso_framework/
│       │
│       ├── __init__.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── model.py
│       │   ├── context.py
│       │   └── runner.py
│       │
│       ├── config/
│       │   ├── __init__.py
│       │   ├── loader.py
│       │   ├── models.py
│       │   └── providers.py
│       │
│       ├── spark/
│       │   ├── __init__.py
│       │   ├── session.py
│       │   ├── reader.py
│       │   └── writer.py
│       │
│       ├── logging/
│       │   ├── __init__.py
│       │   ├── logger.py
│       │   └── context.py
│       │
│       ├── errors/
│       │   ├── __init__.py
│       │   ├── exceptions.py
│       │   └── handlers.py
│       │
│       ├── secrets/
│       │   ├── __init__.py
│       │   └── provider.py
│       │
│       ├── validation/
│       │   ├── __init__.py
│       │   ├── schema.py
│       │   ├── data_quality.py
│       │   └── thresholds.py
│       │
│       ├── audit/
│       │   ├── __init__.py
│       │   └── audit.py
│       │
│       └── utils/
│           ├── __init__.py
│           └── dataframe.py
│
├── models/
│   │
│   └── emissions_counting/
│       ├── __init__.py
│       │
│       ├── config/
│       │   ├── dev.yml
│       │   ├── test.yml
│       │   └── prod.yml
│       │
│       ├── transformations/
│       │   ├── __init__.py
│       │   ├── preparation.py
│       │   └── calculation.py
│       │
│       ├── validation/
│       │   ├── __init__.py
│       │   └── validation.py
│       │
│       └── main.py
│
├── tests/
│   ├── unit/
│   │   ├── framework/
│   │   └── models/
│   │       └── emissions_counting/
│   │
│   └── integration/
│       └── emissions_counting/
│
├── resources/
│   └── jobs/
│       └── emissions_counting.yml
│
├── docs/
│   ├── architecture.md
│   ├── development_standards.md
│   └── onboarding.md
│
├── .gitignore
├── pyproject.toml
├── databricks.yml
└── README.md
