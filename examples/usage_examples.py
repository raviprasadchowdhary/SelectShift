"""
Example usage script for the Oracle to Azure SQL converter.
Demonstrates how to use the converter in Python code.
"""

from oracle_to_azure_select_converter import convert_oracle_select_to_azure


def example_basic_conversion():
    """Example 1: Basic function conversions."""
    print("=" * 70)
    print("Example 1: Basic Function Conversions")
    print("=" * 70)
    
    oracle_query = """
    SELECT 
        employee_id,
        NVL(first_name, 'Unknown') AS first_name,
        NVL(last_name, 'Unknown') AS last_name,
        SYSDATE AS query_date
    FROM employees
    """
    
    print("\nOracle Query:")
    print(oracle_query)
    
    converted, warnings = convert_oracle_select_to_azure(oracle_query)
    
    print("\nAzure SQL Query:")
    print(converted)
    
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  {w}")
    print()


def example_decode_conversion():
    """Example 2: DECODE to CASE conversion."""
    print("=" * 70)
    print("Example 2: DECODE to CASE Conversion")
    print("=" * 70)
    
    oracle_query = """
    SELECT 
        employee_id,
        DECODE(status, 
            'A', 'Active',
            'I', 'Inactive',
            'T', 'Terminated',
            'Unknown') AS status_description,
        DECODE(grade, 1, 'Junior', 2, 'Senior', 3, 'Lead') AS level
    FROM employees
    """
    
    print("\nOracle Query:")
    print(oracle_query)
    
    converted, warnings = convert_oracle_select_to_azure(oracle_query)
    
    print("\nAzure SQL Query:")
    print(converted)
    
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  {w}")
    print()


def example_rownum_conversion():
    """Example 3: ROWNUM to TOP conversion with warning."""
    print("=" * 70)
    print("Example 3: ROWNUM to TOP (with warning)")
    print("=" * 70)
    
    oracle_query = """
    SELECT 
        employee_id,
        first_name,
        last_name,
        salary
    FROM employees
    WHERE ROWNUM <= 10
    ORDER BY salary DESC
    """
    
    print("\nOracle Query:")
    print(oracle_query)
    
    converted, warnings = convert_oracle_select_to_azure(oracle_query)
    
    print("\nAzure SQL Query:")
    print(converted)
    
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  {w}")
    print()


def example_complex_query():
    """Example 4: Complex query with multiple conversions."""
    print("=" * 70)
    print("Example 4: Complex Query with Multiple Conversions")
    print("=" * 70)
    
    oracle_query = """
    SELECT 
        e.employee_id,
        NVL(e.first_name, 'N/A') || ' ' || NVL(e.last_name, 'N/A') AS full_name,
        DECODE(e.status, 'A', 'Active', 'I', 'Inactive', 'Unknown') AS status,
        TRUNC(e.hire_date) AS hire_date,
        TRUNC(SYSDATE) - TRUNC(e.hire_date) AS days_employed,
        d.department_name
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.department_id
    WHERE TRUNC(e.hire_date) >= TRUNC(SYSDATE) - 365
        AND e.status = 'A'
        AND ROWNUM <= 50
    ORDER BY e.hire_date DESC
    """
    
    print("\nOracle Query:")
    print(oracle_query)
    
    converted, warnings = convert_oracle_select_to_azure(oracle_query)
    
    print("\nAzure SQL Query:")
    print(converted)
    
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  {w}")
    print()


def example_with_warnings():
    """Example 5: Query that generates multiple warnings."""
    print("=" * 70)
    print("Example 5: Query with Multiple Warnings")
    print("=" * 70)
    
    oracle_query = """
    SELECT 
        employee_id,
        first_name,
        salary
    FROM employees
    WHERE salary > (
        SELECT AVG(salary) 
        FROM employees 
        WHERE department_id = employees.department_id
    )
    AND ROWNUM <= 10
    ORDER BY salary DESC
    CONNECT BY PRIOR employee_id = manager_id
    """
    
    print("\nOracle Query:")
    print(oracle_query)
    
    converted, warnings = convert_oracle_select_to_azure(oracle_query)
    
    print("\nAzure SQL Query:")
    print(converted)
    
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  {w}")
    print()


if __name__ == '__main__':
    print("\n")
    print("*" * 70)
    print("Oracle to Azure SQL SELECT Query Converter - Examples")
    print("*" * 70)
    print("\n")
    
    example_basic_conversion()
    example_decode_conversion()
    example_rownum_conversion()
    example_complex_query()
    example_with_warnings()
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
