"""
Unit tests for Oracle to Azure SQL SELECT query converter.
"""

import pytest
from oracle_to_azure_select_converter import convert_oracle_select_to_azure


class TestBasicConversions:
    """Test basic SQL function conversions."""
    
    def test_nvl_conversion(self):
        """Test NVL to ISNULL conversion."""
        query = "SELECT NVL(column_name, 'default') FROM table1"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert "ISNULL(column_name, 'default')" in converted
        assert "NVL" not in converted.upper()
    
    def test_nvl_nested(self):
        """Test nested NVL conversion."""
        query = "SELECT NVL(NVL(col1, col2), 'default') FROM table1"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert "ISNULL(ISNULL(col1, col2), 'default')" in converted
    
    def test_sysdate_conversion(self):
        """Test SYSDATE to GETDATE() conversion."""
        query = "SELECT * FROM orders WHERE order_date > SYSDATE - 7"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert "GETDATE()" in converted
        assert "SYSDATE" not in converted.upper()
    
    def test_sysdate_case_insensitive(self):
        """Test SYSDATE conversion is case-insensitive."""
        query = "SELECT sysdate, SYSDATE, SysDate FROM DUAL"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert converted.count("GETDATE()") == 3
    
    def test_string_concatenation(self):
        """Test || to + conversion for string concatenation."""
        query = "SELECT first_name || ' ' || last_name AS full_name FROM employees"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert "first_name + ' ' + last_name" in converted
        assert "||" not in converted
    
    def test_from_dual_removal(self):
        """Test FROM DUAL removal."""
        query = "SELECT SYSDATE FROM DUAL"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert "FROM DUAL" not in converted.upper()
        assert "GETDATE()" in converted
    
    def test_from_dual_case_insensitive(self):
        """Test FROM DUAL removal is case-insensitive."""
        query = "SELECT 1 FROM dual"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert "FROM" not in converted.upper() or "DUAL" not in converted.upper()
    
    def test_trunc_date_conversion(self):
        """Test TRUNC(date) to CAST(date AS DATE) conversion."""
        query = "SELECT * FROM orders WHERE TRUNC(order_date) = TRUNC(SYSDATE)"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert "CAST(order_date AS DATE)" in converted
        assert "CAST(GETDATE() AS DATE)" in converted
        assert "TRUNC" not in converted.upper()


class TestDecodeConversion:
    """Test DECODE to CASE conversion."""
    
    def test_decode_simple(self):
        """Test simple DECODE conversion."""
        query = "SELECT DECODE(status, 'A', 'Active', 'I', 'Inactive', 'Unknown') FROM table1"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert "CASE" in converted.upper()
        assert "WHEN status = 'A' THEN 'Active'" in converted
        assert "WHEN status = 'I' THEN 'Inactive'" in converted
        assert "ELSE 'Unknown'" in converted
        assert "END" in converted.upper()
    
    def test_decode_no_default(self):
        """Test DECODE without default value."""
        query = "SELECT DECODE(code, 1, 'One', 2, 'Two') FROM table1"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert "CASE" in converted.upper()
        assert "WHEN code = 1 THEN 'One'" in converted
        assert "WHEN code = 2 THEN 'Two'" in converted
        assert "END" in converted.upper()


class TestRownumConversion:
    """Test ROWNUM to TOP conversion."""
    
    def test_rownum_less_than_equal(self):
        """Test ROWNUM <= N to TOP N conversion."""
        query = "SELECT * FROM employees WHERE ROWNUM <= 10"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert "SELECT TOP 10" in converted.upper()
        assert "ROWNUM" not in converted.upper()
    
    def test_rownum_less_than(self):
        """Test ROWNUM < N to TOP N-1 conversion."""
        query = "SELECT * FROM employees WHERE ROWNUM < 5"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert "SELECT TOP 4" in converted.upper()
        assert "ROWNUM" not in converted.upper()
    
    def test_rownum_with_order_by_warning(self):
        """Test that ROWNUM with ORDER BY generates warning."""
        query = "SELECT * FROM employees WHERE ROWNUM <= 10 ORDER BY salary DESC"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert len(warnings) > 0
        assert any("ROWNUM" in str(w) and "ORDER BY" in str(w) for w in warnings)


class TestWarnings:
    """Test warning detection."""
    
    def test_connect_by_warning(self):
        """Test CONNECT BY generates warning."""
        query = "SELECT * FROM employees CONNECT BY PRIOR employee_id = manager_id"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert len(warnings) > 0
        assert any("CONNECT BY" in str(w) for w in warnings)
    
    def test_correlated_subquery_warning(self):
        """Test correlated subquery generates warning."""
        query = """
        SELECT e.name 
        FROM employees e 
        WHERE e.salary > (SELECT AVG(salary) FROM employees WHERE dept_id = e.dept_id)
        """
        converted, warnings = convert_oracle_select_to_azure(query)
        assert len(warnings) > 0
        assert any("subquery" in str(w).lower() for w in warnings)
    
    def test_non_select_query_warning(self):
        """Test non-SELECT query generates warning."""
        query = "INSERT INTO employees VALUES (1, 'John')"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert len(warnings) > 0
        assert any("SELECT" in str(w) for w in warnings)


class TestComplexQueries:
    """Test complex real-world query conversions."""
    
    def test_complex_query_with_multiple_conversions(self):
        """Test query with multiple conversion rules."""
        query = """
        SELECT 
            employee_id,
            NVL(first_name, 'N/A') || ' ' || NVL(last_name, 'N/A') AS full_name,
            DECODE(status, 'A', 'Active', 'I', 'Inactive', 'Unknown') AS status_desc,
            TRUNC(hire_date) AS hire_date_only
        FROM employees
        WHERE TRUNC(hire_date) >= TRUNC(SYSDATE) - 30
            AND ROWNUM <= 100
        ORDER BY hire_date DESC
        """
        converted, warnings = convert_oracle_select_to_azure(query)
        
        # Check all conversions applied
        assert "ISNULL" in converted.upper()
        assert "+" in converted  # String concatenation
        assert "CASE" in converted.upper()
        assert "CAST" in converted.upper() and "AS DATE" in converted.upper()
        assert "GETDATE()" in converted
        assert "SELECT TOP 100" in converted.upper()
        
        # Should have warning for ROWNUM with ORDER BY
        assert len(warnings) > 0
    
    def test_preserves_formatting(self):
        """Test that formatting is preserved where possible."""
        query = """SELECT 
    column1,
    column2
FROM table1"""
        converted, warnings = convert_oracle_select_to_azure(query)
        # Should maintain multi-line structure
        assert "\n" in converted


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_query(self):
        """Test empty query handling."""
        query = ""
        converted, warnings = convert_oracle_select_to_azure(query)
        assert len(warnings) > 0
    
    def test_with_cte(self):
        """Test WITH clause (CTE) support."""
        query = """
        WITH dept_avg AS (
            SELECT dept_id, AVG(salary) as avg_sal FROM employees GROUP BY dept_id
        )
        SELECT * FROM dept_avg
        """
        converted, warnings = convert_oracle_select_to_azure(query)
        assert "WITH" in converted.upper()
        # Should not generate non-SELECT warning
        select_warnings = [w for w in warnings if "SELECT" in str(w) and "does not appear" in str(w)]
        assert len(select_warnings) == 0
    
    def test_multiple_nvl_in_same_line(self):
        """Test multiple NVL calls on same line."""
        query = "SELECT NVL(col1, 0) + NVL(col2, 0) AS total FROM table1"
        converted, warnings = convert_oracle_select_to_azure(query)
        assert converted.count("ISNULL") == 2
        assert "NVL" not in converted.upper()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
