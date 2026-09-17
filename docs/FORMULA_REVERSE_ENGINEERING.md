# SME Formula Reverse Engineering

The Excel model is the current implementation and SMEs are reverse engineering its formulas.

For every formula capture:

| Field | Required |
|---|---|
| formula_id | Yes |
| business name | Yes |
| source datasets/columns | Yes |
| Excel sheet/cell/range | Yes |
| formula | Yes |
| input units | Yes |
| output units | Yes |
| emission factors/lookups | Yes |
| assumptions | Yes |
| scenario logic | Yes |
| SME owner | Yes |
| formula version | Yes |
| approval status | Yes |

## Rule

Do not guess missing business logic.

Unknown logic becomes a discovery item until an SME confirms it.

## Regression

For each approved formula:

```text
Approved Excel input
        |
        +--> Excel expected result
        |
        +--> PySpark result
                |
                v
          tolerance comparison
                |
                v
          SME sign-off
```

The comparison becomes a permanent regression test.
