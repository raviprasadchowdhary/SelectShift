# Oracle ↔ Azure SQL SELECT Query Converter

A QA support tool for **bidirectional** conversion between Oracle and Azure SQL / SQL Server SELECT queries.

## 🎯 Purpose

This tool is **NOT a migration engine**. It's a **QA accelerator** designed to help QA testers after database migration:

- ✅ Quickly convert queries between Oracle and Azure SQL (bidirectional)
- ✅ Compare query results between source and target databases  
- ✅ Detect syntax and logic differences
- ✅ **GUI interface** for easy conversion without coding

## 🖥️ NEW: GUI Application

**Launch the graphical interface:**
```powershell
python run_gui.py
```

**Features:**
- Two-panel layout (Oracle ↔ Azure SQL)
- Convert in either direction with one click
- Visual warning display
- Swap queries between panels
- No coding required!

See **[GUI_GUIDE.md](GUI_GUIDE.md)** for detailed GUI instructions.

## 📋 Features

### ✅ Supported Conversions

The tool performs deterministic, safe conversions for:

**Oracle → Azure SQL:**

| Oracle Syntax | Azure SQL Equivalent | Description |
|--------------|---------------------|-------------|
| `NVL(a, b)` | `ISNULL(a, b)` | Null value replacement |
| `DECODE(expr, ...)` | `CASE WHEN ... END` | Conditional logic |
| `SYSDATE` | `GETDATE()` | Current date/time |
| `FROM DUAL` | _(removed)_ | Dummy table not needed |
| `\|\|` (concatenation) | `+` | String concatenation |
| `TRUNC(date_col)` | `CAST(date_col AS DATE)` | Date truncation |
| `WHERE ROWNUM <= N` | `SELECT TOP N` | Row limiting |

**Azure SQL → Oracle:**

| Azure SQL Syntax | Oracle Equivalent | Description |
|-----------------|-------------------|-------------|
| `ISNULL(a, b)` | `NVL(a, b)` | Null value replacement |
| `GETDATE()` | `SYSDATE` | Current date/time |
| `+` (concatenation) | `\|\|` | String concatenation |
| `CAST(date AS DATE)` | `TRUNC(date)` | Date truncation |
| `SELECT TOP N` | `WHERE ROWNUM <= N` | Row limiting |

### ⚠️ Warning Detection

The tool warns (does not blindly convert) for complex features:

- `CONNECT BY` - Hierarchical queries
- `ROWNUM` with `ORDER BY` - Pagination issues
- Complex date arithmetic
- Correlated subqueries

## 🚀 Installation

```powershell
# Clone the repository
cd c:\Users\916992\github\SelectShift

# Install dependencies (optional, for tests)
pip install pytest
```

**No additional dependencies needed for the GUI** - tkinter is included with Python!

### 📦 Deployment Options

**Option 1: Run with Python** (Current - requires Python 3.7+)
```powershell
python run_gui.py
```

**Option 2: Standalone Executable** (No Python required!)
```powershell
# Build once:
pip install pyinstaller
pyinstaller oracle_azure_converter.spec

# Distribute:
dist/OracleAzureConverter.exe  ← Share this with QA testers!
```

See **[BUILD_EXECUTABLE.md](BUILD_EXECUTABLE.md)** for detailed instructions on creating a standalone .exe that doesn't require Python installation.

## 📖 Usage

### 🖥️ GUI Application (Recommended for QA Testers)

```powershell
python run_gui.py
```

**Benefits:**
- Visual interface - no coding required
- Two-panel layout for side-by-side comparison
- Bidirectional conversion (Oracle ↔ Azure)
- Instant warning display
- Swap and clear functions

### Python API

**Oracle → Azure:**
```python
from oracle_to_azure_select_converter import convert_oracle_select_to_azure

oracle_query = """
    SELECT 
        employee_id,
        NVL(first_name, 'N/A') || ' ' || last_name AS full_name,
        DECODE(status, 'A', 'Active', 'I', 'Inactive') AS status_desc
    FROM employees
    WHERE ROWNUM <= 10
"""

converted_query, warnings = convert_oracle_select_to_azure(oracle_query)
print(converted_query)
for warning in warnings:
    print(warning)
```

**Azure → Oracle:**
```python
from oracle_to_azure_select_converter import convert_azure_select_to_oracle

azure_query = """
    SELECT TOP 10
        employee_id,
        ISNULL(first_name, 'N/A') + ' ' + last_name AS full_name,
        CASE WHEN status = 'A' THEN 'Active' END AS status_desc
    FROM employees
"""

converted_query, warnings = convert_azure_select_to_oracle(azure_query)
print(converted_query)
```

**Output:**
```sql
SELECT TOP 10 
    employee_id,
    ISNULL(first_name, 'N/A') + ' ' + last_name AS full_name,
    CASE WHEN status = 'A' THEN 'Active' WHEN status = 'I' THEN 'Inactive' END AS status_desc
FROM employees
```

### Command-Line Interface

```powershell
# Convert a query string
python -m oracle_to_azure_select_converter -q "SELECT NVL(name, 'Unknown') FROM DUAL"

# Convert from file
python -m oracle_to_azure_select_converter -f input_query.sql

# Save to output file
python -m oracle_to_azure_select_converter -f oracle_query.sql -o azure_query.sql

# Suppress warnings
python -m oracle_to_azure_select_converter -f query.sql --no-warnings
```

## 📚 Examples

### Example 1: Basic Function Conversions

**Oracle:**
```sql
SELECT 
    NVL(department_name, 'Unassigned') AS dept,
    SYSDATE AS current_date
FROM departments
```

**Azure SQL:**
```sql
SELECT 
    ISNULL(department_name, 'Unassigned') AS dept,
    GETDATE() AS current_date
FROM departments
```

### Example 2: DECODE to CASE

**Oracle:**
```sql
SELECT 
    employee_id,
    DECODE(grade, 1, 'Junior', 2, 'Senior', 3, 'Lead', 'Other') AS level
FROM employees
```

**Azure SQL:**
```sql
SELECT 
    employee_id,
    CASE WHEN grade = 1 THEN 'Junior' WHEN grade = 2 THEN 'Senior' WHEN grade = 3 THEN 'Lead' ELSE 'Other' END AS level
FROM employees
```

### Example 3: Date Operations

**Oracle:**
```sql
SELECT * 
FROM orders 
WHERE TRUNC(order_date) = TRUNC(SYSDATE)
```

**Azure SQL:**
```sql
SELECT * 
FROM orders 
WHERE CAST(order_date AS DATE) = CAST(GETDATE() AS DATE)
```

### Example 4: Row Limiting with Warning

**Oracle:**
```sql
SELECT * 
FROM employees 
WHERE ROWNUM <= 5 
ORDER BY salary DESC
```

**Azure SQL (with warning):**
```sql
SELECT TOP 5 * 
FROM employees 
ORDER BY salary DESC
```

**Warning:**
```
⚠ WARNING: ROWNUM used with ORDER BY. Manual review required - results may differ. 
Consider using ROW_NUMBER() OVER(ORDER BY ...) instead.
```

## 🔒 Scope & Constraints

### ✅ Supported Operations

- `SELECT` queries
- `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY` clauses
- `JOIN` operations (INNER, LEFT, RIGHT, FULL)
- Subqueries and CTEs (`WITH` clause)

### ❌ NOT Supported

- `INSERT`, `UPDATE`, `DELETE` statements
- Stored procedures
- PL/SQL blocks
- DDL statements (`CREATE`, `ALTER`, `DROP`)
- DML transactions

## 🧪 Testing

Run the comprehensive test suite:

```powershell
# Run all tests
pytest tests/test_converter.py -v

# Run specific test class
pytest tests/test_converter.py::TestBasicConversions -v

# Run with coverage
pytest tests/test_converter.py --cov=oracle_to_azure_select_converter
```

## 🏗️ Architecture

```
oracle_to_azure_select_converter/
├── __init__.py          # Package initialization
├── converter.py         # Core conversion logic
├── cli.py              # Command-line interface
└── __main__.py         # CLI entry point

tests/
└── test_converter.py   # Comprehensive test suite
```

### Key Components

- **`OracleToAzureConverter`**: Main conversion class with modular methods
- **`ConversionWarning`**: Warning objects for complex features
- **`convert_oracle_select_to_azure()`**: Public API function

## 🔧 Extending the Tool

To add a new conversion rule:

1. Add a method to `OracleToAzureConverter` class:
```python
def _convert_new_function(self, query: str) -> str:
    """Convert Oracle NEW_FUNC to Azure equivalent."""
    # Implementation with regex
    return converted_query
```

2. Call it in the `convert()` method:
```python
converted = self._convert_new_function(converted)
```

3. Add tests in `tests/test_converter.py`

## ⚠️ Important Notes

1. **Manual Review Required**: Always review converted queries, especially those with warnings
2. **Test Thoroughly**: Compare results between Oracle and Azure SQL for accuracy
3. **Performance**: Row limiting behavior differs between `ROWNUM` and `TOP`
4. **Nested Functions**: Complex nested functions may need manual adjustment

## 📄 License

This is an internal QA tool. Use at your own discretion.

## 🤝 Contributing

This is a working MVP. Contributions welcome:
- Add new conversion rules
- Improve regex patterns
- Enhance warning detection
- Add more test cases

## 📞 Support

For issues or questions, contact the database migration QA team.

---

**Version:** 1.0.0  
**Author:** Database Migration & QA Team  
**Last Updated:** January 2026
