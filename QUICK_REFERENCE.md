# Oracle to Azure SQL - Quick Reference Card

## Automatic Conversions (15 Total)

### Functions

| Oracle | Azure SQL | Status |
|--------|-----------|--------|
| `NVL(a, b)` | `ISNULL(a, b)` | ✅ Auto |
| `DECODE(x, a, b, c)` | `CASE WHEN x = a THEN b ELSE c END` | ✅ Auto |
| `SYSDATE` | `GETDATE()` | ✅ Auto |
| `TRUNC(date)` | `CAST(date AS DATE)` | ✅ Auto |
| `ADD_MONTHS(date, n)` | `DATEADD(MONTH, n, date)` | ✅ Auto |
| `SUBSTR(str, pos, len)` | `SUBSTRING(str, pos, len)` | ✅ Auto |
| `TO_CHAR(date, 'YYYY-MM-DD')` | `CONVERT(VARCHAR(10), date, 120)` | ✅ Auto |
| `LISTAGG(col, delim)` | **Manual** - Use `STRING_AGG(col, delim)` | ⚠️ Warning |
| `REGEXP_LIKE(col, pattern)` | **Manual** - Use `LIKE` or CLR | ⚠️ Warning |

### Operators & Syntax

| Oracle | Azure SQL | Status |
|--------|-----------|--------|
| `\|\|` (concat) | `+` | ✅ Auto |
| `FROM DUAL` | *removed* | ✅ Auto |
| `WHERE ROWNUM <= N` | `SELECT TOP N` | ✅ Auto |
| `FETCH FIRST N ROWS ONLY` | `OFFSET 0 ROWS FETCH NEXT N ROWS ONLY` | ✅ Auto |
| `/*+ optimizer_hint */` | *removed* | ✅ Auto + Warning |

### HTML Entities

| Oracle | Azure SQL | Status |
|--------|-----------|--------|
| `&gt;` | `>` | ✅ Auto |
| `&lt;` | `<` | ✅ Auto |
| `&amp;` | `&` | ✅ Auto |
| `&quot;` | `"` | ✅ Auto |

---

## Common Patterns

### Pattern 1: Date Calculations
```sql
-- Oracle
ADD_MONTHS(hire_date, 3)

-- Azure SQL
DATEADD(MONTH, 3, hire_date)
```

### Pattern 2: Nested NVL
```sql
-- Oracle
NVL(NVL(col1, col2), 0)

-- Azure SQL
ISNULL(ISNULL(col1, col2), 0)
```

### Pattern 3: String Concatenation
```sql
-- Oracle
first_name || ' ' || last_name

-- Azure SQL
first_name + ' ' + last_name
```

### Pattern 4: Date Truncation
```sql
-- Oracle
TRUNC(SYSDATE)

-- Azure SQL
CAST(GETDATE() AS DATE)
```

### Pattern 5: DECODE to CASE
```sql
-- Oracle
DECODE(status, 'A', 'Active', 'I', 'Inactive', 'Unknown')

-- Azure SQL
CASE WHEN status = 'A' THEN 'Active' 
     WHEN status = 'I' THEN 'Inactive' 
     ELSE 'Unknown' END
```

### Pattern 6: Top N Rows
```sql
-- Oracle
SELECT * FROM employees WHERE ROWNUM <= 10

-- Azure SQL
SELECT TOP 10 * FROM employees
```

### Pattern 7: Fetch First
```sql
-- Oracle
SELECT * FROM employees ORDER BY salary DESC FETCH FIRST 10 ROWS ONLY

-- Azure SQL
SELECT * FROM employees ORDER BY salary DESC OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY
```

---

## Warnings Generated

The tool generates warnings for features that require manual review:

| Warning | Meaning | Action Required |
|---------|---------|-----------------|
| `CONNECT BY` | Hierarchical query | Convert to CTE/recursive query |
| `ROWNUM with ORDER BY` | Pagination issue | Use `ROW_NUMBER() OVER(ORDER BY ...)` |
| `Complex date arithmetic` | Date calculations | Verify `DATEADD()` is correct |
| `Correlated subquery` | Subquery with outer reference | Verify logic after conversion |
| `LISTAGG` | List aggregation | Use `STRING_AGG()` (SQL Server 2017+) |
| `REGEXP_LIKE` | Regex matching | Use `LIKE` or custom CLR function |
| `OPTIMIZER_HINTS` | Query optimizer hints | Consider Azure SQL query hints or indexes |

---

## Usage

1. **Paste Oracle query** in left panel
2. **Click "Convert to Azure SQL"**
3. **Review warnings** (if any)
4. **Copy converted query** from right panel
5. **Test in Azure SQL** environment
6. **Manually adjust** any warned features

---

## Tips

✅ **Always test** converted queries in your Azure SQL environment  
✅ **Review warnings** carefully - they indicate features needing manual conversion  
✅ **Check performance** - Azure SQL may benefit from different indexes  
✅ **Use Swap button** to reverse convert (Azure → Oracle)  
✅ **Preserve comments** - `/* */` and `--` comments are maintained  

---

## What's NOT Converted Automatically

❌ **PL/SQL blocks** (procedures, functions, packages)  
❌ **DDL statements** (CREATE, ALTER, DROP)  
❌ **DML statements** (INSERT, UPDATE, DELETE, MERGE)  
❌ **CONNECT BY** hierarchical queries  
❌ **Complex ROWNUM** pagination (with ORDER BY)  
❌ **Oracle-specific packages** (DBMS_*, UTL_*)  
❌ **Sequences** (use IDENTITY or SEQUENCE in Azure SQL)  
❌ **DUAL-based calculations** beyond simple SELECT  

---

## Support

This is a **QA support tool** for converting **read-only Oracle SELECT queries** to **Azure SQL format**.

**Scope:** SELECT statements only  
**Goal:** Deterministic, safe conversions with warnings for complex features  
**Use Case:** Quality Assurance, testing, query migration  

---

## Files

- `OracleAzureConverter.exe` - Standalone executable (10.69 MB)
- `NEW_FEATURES.md` - Detailed feature documentation
- `TEST_RESULTS.md` - Test results and examples
- `README.md` - Project overview
