# QA Checklist Tool

Automated quality assurance checks for Oracle to Azure SQL conversions.

## Usage

### Quick Check (Python)

```python
from qa_checklist import quick_qa

oracle_query = """
SELECT NVL(name, 'N/A'), TRUNC(hire_date)
FROM employees
WHERE dept_id &gt; 10
"""

quick_qa(oracle_query)
```

### Programmatic Use

```python
from qa_checklist import run_qa_checklist
from oracle_to_azure_select_converter import convert_oracle_select_to_azure

# Convert query
converted_sql, warnings = convert_oracle_select_to_azure(oracle_query)

# Run QA checks
results = run_qa_checklist(converted_sql, warnings)

# Check results
if results['_summary']['overall_status'] == 'PASS':
    print("Ready for execution!")
else:
    print("Manual fixes required")
```

## QA Checks Performed

### 1. **No HTML Entities Remain** (CRITICAL)
- Checks: `&gt;`, `&lt;`, `&amp;`, `&quot;`, `&apos;`, `&nbsp;`
- Status: PASS if all entities decoded, FAIL if any remain
- Severity: CRITICAL (will cause syntax errors)

### 2. **No Oracle-Only Functions Remain** (CRITICAL)
- Checks for: `NVL`, `DECODE`, `TRUNC`, `ADD_MONTHS`, `SUBSTR`, `TO_CHAR`, `LISTAGG`, `SYSDATE`, `ROWNUM`
- Status: PASS if all converted, FAIL if any remain
- Severity: CRITICAL (not supported in SQL Server)
- Note: Ignores functions in comments

### 3. **STRING_AGG with DISTINCT Uses Derived Set** (WARNING)
- Checks: `STRING_AGG` with `SELECT DISTINCT` pattern
- Status: 
  - PASS if pattern correct and no placeholder
  - FAIL if `<source_table>` placeholder present (manual fix required)
  - PASS if no STRING_AGG in query
- Severity: WARNING (requires manual completion)
- Action: Replace `<source_table>` with actual table/CTE + add WHERE correlation

### 4. **REGEXP_LIKE Handling** (WARNING)
- Checks: Native function used with version warning/comment
- Status: PASS if warning present, FAIL if missing
- Severity: WARNING (version-dependent)
- Note: SQL Server 2025+ / Azure SQL compat ≥ 170 required for native function

### 5. **Basic Syntax Checks** (CRITICAL)
- Checks:
  - No HTML entities in operators
  - Balanced parentheses
  - Contains SELECT keyword
- Status: PASS if all checks pass
- Severity: CRITICAL (will cause execution errors)

## Output Example

```
================================================================================
QA CHECKLIST REPORT
================================================================================

[PASS] HTML ENTITIES
    Status: OK
    No HTML entities remain

[PASS] ORACLE FUNCTIONS
    Status: OK
    All Oracle functions converted

[FAIL] STRING AGG DISTINCT
    Status: WARNING
    STRING_AGG DISTINCT pattern found but requires manual fix (replace <source_table> placeholder)
    ACTION: Replace <source_table> with actual table/CTE and add WHERE correlation

[PASS] REGEXP LIKE
    Status: OK
    REGEXP_LIKE uses native function with version warning

[PASS] SYNTAX
    Status: OK
    Basic syntax checks passed

================================================================================
SUMMARY
================================================================================
Total Checks: 5
Passed: 4
Critical Failures: 0
Warnings: 1

Overall Status: PASS
Ready for SSMS/Azure SQL Execution: NO (manual fixes required)
================================================================================
```

## Integration into Workflow

### Recommended Workflow

1. **Convert** Oracle query using converter
2. **Run QA** checks using `quick_qa()` or `run_qa_checklist()`
3. **Fix warnings** (e.g., replace LISTAGG placeholders)
4. **Execute** in SSMS/Azure SQL
5. **Verify results** match Oracle baseline on golden dataset

### CI/CD Integration

```python
results = run_qa_checklist(converted_sql, warnings)

# Fail build on critical errors
if results['_summary']['critical_failures'] > 0:
    sys.exit(1)

# Warn on manual fixes required
if results['_summary']['warnings'] > 0:
    print("Warning: Manual fixes required before execution")
```

## Manual Fixes Required

### LISTAGG(DISTINCT) Placeholder

**Generated:**
```sql
(SELECT STRING_AGG(x.dx3, ',') WITHIN GROUP (ORDER BY x.dx3)
 FROM (SELECT DISTINCT rc.dx3 FROM <source_table>) AS x)
```

**Manual fix:**
```sql
(SELECT STRING_AGG(x.dx3, ',') WITHIN GROUP (ORDER BY x.dx3)
 FROM (SELECT DISTINCT rc2.dx3 
       FROM recent_claims AS rc2 
       WHERE rc2.member_id = rc.member_id) AS x)
```

Steps:
1. Replace `<source_table>` with actual table/CTE name
2. Add appropriate alias (e.g., `AS rc2`)
3. Add WHERE clause correlating to outer query's grouping key

## Running from Command Line

```bash
python qa_checklist.py
```

This runs the built-in example query and displays the QA report.

## Status Interpretation

| Overall Status | Meaning | Action |
|---------------|---------|--------|
| PASS (0 warnings) | Ready for execution | Run in SSMS/Azure SQL |
| PASS (with warnings) | Mostly correct, manual fixes needed | Complete manual steps, then execute |
| FAIL | Critical errors present | Review and fix before attempting execution |

## Notes

- **HTML entities:** Must be zero for query to parse
- **Oracle functions:** Must be zero for query to execute
- **LISTAGG placeholders:** Safe to execute after manual completion
- **REGEXP_LIKE:** Verify SQL Server version supports native function
- **Syntax checks:** Basic validation only; not a full SQL parser

## See Also

- `STATUS_REPORT.md` - Implementation status of all fixes
- `ADDRESSING_USER_REQUIREMENTS.md` - Detailed technical documentation
- `converter.py` - Core conversion logic
