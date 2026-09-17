# Dependency Policy

1. Runtime dependencies are centrally declared.
2. Production dependency versions must be security-approved.
3. PySpark must match the approved Databricks Runtime/Spark compatibility.
4. Dependency upgrades require CI regression tests.
5. Do not add a library for functionality already available in Spark/Python without justification.
6. Do not commit generated virtual environments or package caches.
