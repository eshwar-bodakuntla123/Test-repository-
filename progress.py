model-platform/
│
├── src/
│   └── framework/
│       │
│       ├── core/
│       │   ├── model.py
│       │   ├── context.py
│       │   └── runner.py
│       │
│       ├── config/
│       │   ├── loader.py
│       │   ├── models.py
│       │   └── providers.py
│       │
│       ├── spark/
│       │   ├── session.py
│       │   ├── reader.py
│       │   └── writer.py
│       │
│       ├── logging/
│       │   ├── logger.py
│       │   └── context.py
│       │
│       ├── errors/
│       │   ├── exceptions.py
│       │   └── handlers.py
│       │
│       ├── secrets/
│       │   └── provider.py
│       │
│       ├── validation/
│       │   ├── schema.py
│       │   ├── data_quality.py
│       │   └── thresholds.py
│       │
│       ├── audit/
│       │   └── audit.py
│       │
│       └── utils/
│           └── dataframe.py
│
├── models/
│   │
│   └── counting/
│       │
│       ├── config/
│       │   ├── dev.yml
│       │   ├── test.yml
│       │   └── prod.yml
│       │
│       ├── transformations/
│       │   ├── preparation.py
│       │   └── calculation.py
│       │
│       ├── validation/
│       │   └── validation.py
│       │
│       └── main.py
│
├── tests/
│   │
│   ├── unit/
│   │   ├── framework/
│   │   └── models/
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