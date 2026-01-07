# New Conversion Features - Update Summary

## Version Update
**Date:** 2025-01-XX  
**Executable:** OracleAzureConverter.exe (10.69 MB)

---

## ✅ 8 New Conversion Features Added

### 1. **HTML Entity Decoding**
- **What:** Automatically decodes HTML entities in queries
- **Conversion:** `&gt;` → `>`, `&lt;` → `<`, `&amp;` → `&`, `&quot;` → `"`
- **Example:**
  ```sql
  -- Oracle (with HTML entities)
  SELECT * FROM table WHERE value &gt; 100 AND value &lt; 200
  
  -- Azure SQL
  SELECT * FROM table WHERE value > 100 AND value < 200
  ```

### 2. **ADD_MONTHS Function**
- **What:** Converts Oracle `ADD_MONTHS()` to SQL Server `DATEADD()`
- **Conversion:** `ADD_MONTHS(date, n)` → `DATEADD(MONTH, n, date)`
- **Special handling:** Detects year calculations like `-12 * 18` → `DATEADD(YEAR, -18, date)`
- **Example:**
  ```sql
  -- Oracle
  SELECT ADD_MONTHS(hire_date, 3) FROM employees
  
  -- Azure SQL
  SELECT DATEADD(MONTH, 3, hire_date) FROM employees
  ```

### 3. **SUBSTR Function**
- **What:** Converts Oracle `SUBSTR()` to SQL Server `SUBSTRING()`
- **Conversion:** `SUBSTR(string, start, length)` → `SUBSTRING(string, start, length)`
- **Example:**
  ```sql
  -- Oracle
  SELECT SUBSTR(name, 1, 5) FROM employees
  
  -- Azure SQL
  SELECT SUBSTRING(name, 1, 5) FROM employees
  ```

### 4. **TO_CHAR Date Formatting**
- **What:** Converts Oracle `TO_CHAR()` date formatting to SQL Server `CONVERT()` or `FORMAT()`
- **Conversion:** 
  - `TO_CHAR(date, 'YYYY-MM-DD')` → `CONVERT(VARCHAR(10), date, 120)`
  - Other formats → `FORMAT(date, 'format_string')`
- **Example:**
  ```sql
  -- Oracle
  SELECT TO_CHAR(hire_date, 'YYYY-MM-DD') FROM employees
  
  -- Azure SQL
  SELECT CONVERT(VARCHAR(10), hire_date, 120) FROM employees
  ```

### 5. **FETCH FIRST Clause**
- **What:** Converts Oracle `FETCH FIRST` to Azure SQL compatible syntax
- **Conversion:** `FETCH FIRST n ROWS ONLY` → `OFFSET 0 ROWS FETCH NEXT n ROWS ONLY`
- **Note:** Azure SQL requires `OFFSET` before `FETCH`
- **Example:**
  ```sql
  -- Oracle
  SELECT * FROM employees ORDER BY salary DESC FETCH FIRST 10 ROWS ONLY
  
  -- Azure SQL
  SELECT * FROM employees ORDER BY salary DESC OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY
  ```

### 6. **LISTAGG Detection (Warning)**
- **What:** Detects `LISTAGG()` usage and provides conversion guidance
- **Warning:** "LISTAGG detected. SQL Server uses STRING_AGG (2017+). DISTINCT not directly supported - may need subquery."
- **Example:**
  ```sql
  -- Oracle
  SELECT dept_id, LISTAGG(name, ', ') FROM employees GROUP BY dept_id
  
  -- Conversion: Manual conversion required (warning provided)
  -- Suggested Azure SQL equivalent:
  SELECT dept_id, STRING_AGG(name, ', ') FROM employees GROUP BY dept_id
  ```

### 7. **REGEXP_LIKE Detection (Warning)**
- **What:** Detects `REGEXP_LIKE()` usage and provides conversion guidance
- **Warning:** "REGEXP_LIKE detected. SQL Server has no native regex. Consider LIKE with wildcards or custom CLR function."
- **Example:**
  ```sql
  -- Oracle
  SELECT * FROM employees WHERE REGEXP_LIKE(name, '^[A-Z]')
  
  -- Conversion: Manual conversion required (warning provided)
  -- Suggested Azure SQL alternatives:
  -- Option 1: LIKE pattern (limited)
  -- Option 2: Custom CLR function
  ```

### 8. **Optimizer Hints Removal**
- **What:** Removes Oracle optimizer hints and warns about manual review
- **Conversion:** `/*+ hint */` → removed with warning
- **Warning:** "OPTIMIZER_HINTS - Oracle optimizer hints (/*+ ... */) have been removed - Azure SQL does not support them"
- **Example:**
  ```sql
  -- Oracle
  SELECT /*+ INDEX(emp emp_idx) */ * FROM employees
  
  -- Azure SQL
  SELECT  * FROM employees
  -- (Warning: Optimizer hints removed - consider Azure SQL query hints or indexes)
  ```

---

## Previously Existing Features (Still Working)

1. ✅ **NVL → ISNULL** (including nested NVL)
2. ✅ **DECODE → CASE**
3. ✅ **SYSDATE → GETDATE()**
4. ✅ **TRUNC(date) → CAST(date AS DATE)**
5. ✅ **String concatenation:** `||` → `+`
6. ✅ **FROM DUAL** removal
7. ✅ **ROWNUM → TOP N** conversion
8. ✅ **Comment handling** (supports `/* */` and `--` comments)

---

## Technical Improvements

### Performance Enhancements
- 25+ pre-compiled regex patterns for faster matching
- Optimized conversion pipeline with 13 conversion methods
- Efficient nested function handling

### Reliability
- Fixed comment validation bug (queries starting with `/* */` now work correctly)
- Proper parentheses matching for nested function calls
- Comprehensive warning system for features requiring manual review

---

## Testing

All conversions have been tested with:
- Individual test cases for each feature
- Complex 95-line healthcare analytics query
- Nested function calls
- Combined feature usage

**Test Result:** All conversions working correctly ✅

---

## How to Use the New Features

1. **Run the standalone executable:**
   - `OracleAzureConverter.exe` (no installation required)

2. **Paste your Oracle query** in the left panel

3. **Click "Convert to Azure SQL"**

4. **Review warnings** (if any) for features requiring manual review

5. **Copy converted query** from the right panel

6. **Use "Swap" button** to reverse convert Azure SQL back to Oracle (if needed)

---

## Known Limitations

1. **LISTAGG:** Requires manual conversion to `STRING_AGG()` (SQL Server 2017+)
2. **REGEXP_LIKE:** No native regex in SQL Server - requires LIKE patterns or CLR functions
3. **Complex optimizer hints:** May need to be replaced with Azure SQL query hints or index tuning
4. **Nested TO_CHAR:** Some complex format strings may need manual adjustment

---

## File Information

- **Converter Module:** `oracle_to_azure_select_converter/converter.py` (503 lines)
- **GUI Module:** `oracle_to_azure_select_converter/gui.py` (431 lines)
- **Tests:** `tests/test_converter.py` (21 unit tests)
- **Executable:** `dist/OracleAzureConverter.exe` (10.69 MB)

---

## Build Information

**PyInstaller Version:** 6.17.0  
**Python Version:** 3.13.7  
**Build Command:** `python -m PyInstaller --noconfirm --clean oracle_azure_converter.spec`
