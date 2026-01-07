# Quick Start Guide

## Installation & Setup

No installation required! Just use Python 3.7+.

```powershell
cd c:\Users\916992\github\SelectShift
```

## Quick Examples

### 1. Command Line - Simple Query

```powershell
python -m oracle_to_azure_select_converter -q "SELECT SYSDATE FROM DUAL"
```

**Output:**
```sql
SELECT GETDATE()
```

### 2. Command Line - Complex Query

```powershell
python -m oracle_to_azure_select_converter -q "SELECT NVL(name, 'Unknown') || ' ' || dept FROM employees WHERE ROWNUM <= 10"
```

**Output:**
```sql
SELECT TOP 10 ISNULL(name, 'Unknown') + ' ' + dept FROM employees
```

### 3. Python API

```python
from oracle_to_azure_select_converter import convert_oracle_select_to_azure

oracle_query = """
SELECT 
    NVL(first_name, 'N/A') || ' ' || last_name AS full_name,
    DECODE(status, 'A', 'Active', 'I', 'Inactive') AS status,
    TRUNC(hire_date) AS hire_date
FROM employees
WHERE ROWNUM <= 10
"""

converted, warnings = convert_oracle_select_to_azure(oracle_query)
print(converted)
```

**Output:**
```sql
SELECT TOP 10
    ISNULL(first_name, 'N/A') + ' ' + last_name AS full_name,
    CASE WHEN status = 'A' THEN 'Active' WHEN status = 'I' THEN 'Inactive' END AS status,
    CAST(hire_date AS DATE) AS hire_date
FROM employees
```

### 4. File Conversion

```powershell
# Convert and display
python -m oracle_to_azure_select_converter -f my_oracle_query.sql

# Convert and save
python -m oracle_to_azure_select_converter -f oracle_query.sql -o azure_query.sql
```

## Common Conversions

| Oracle | Azure SQL |
|--------|-----------|
| `NVL(col, 'default')` | `ISNULL(col, 'default')` |
| `col1 \|\| col2` | `col1 + col2` |
| `SYSDATE` | `GETDATE()` |
| `FROM DUAL` | _(removed)_ |
| `WHERE ROWNUM <= 10` | `SELECT TOP 10` |
| `TRUNC(date_col)` | `CAST(date_col AS DATE)` |
| `DECODE(x, 'A', 1, 'B', 2, 0)` | `CASE WHEN x='A' THEN 1 WHEN x='B' THEN 2 ELSE 0 END` |

## When You'll See Warnings

The tool warns you about features that need manual review:

- ⚠️ `CONNECT BY` - Hierarchical queries (use CTEs instead)
- ⚠️ `ROWNUM` with `ORDER BY` - Pagination logic differs (consider `ROW_NUMBER()`)
- ⚠️ Correlated subqueries - Verify logic after conversion
- ⚠️ Complex date arithmetic - Check semantic correctness

## Running Tests

```powershell
# Install pytest first (one time)
pip install pytest

# Run tests
pytest tests/test_converter.py -v
```

## Tips for QA Testers

1. **Always review the converted query** before running it
2. **Pay attention to warnings** - they indicate potential issues
3. **Compare results** between Oracle and Azure SQL for accuracy
4. **Start with simple queries** to build confidence
5. **Use file mode** for large queries: `-f input.sql -o output.sql`

## Need Help?

See the full `README.md` for detailed documentation and examples.
