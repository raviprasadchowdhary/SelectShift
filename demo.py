"""
Quick Demo - Oracle to Azure SQL Converter
Run this to see the tool in action!
"""

from oracle_to_azure_select_converter import convert_oracle_select_to_azure


def demo():
    print("=" * 80)
    print(" " * 20 + "ORACLE TO AZURE SQL CONVERTER - DEMO")
    print("=" * 80)
    print()
    
    # Example 1: Simple conversion
    print("📝 Example 1: Basic NVL and String Concatenation")
    print("-" * 80)
    oracle1 = "SELECT NVL(first_name, 'Unknown') || ' ' || last_name FROM employees"
    print(f"Oracle:    {oracle1}")
    azure1, warnings1 = convert_oracle_select_to_azure(oracle1)
    print(f"Azure SQL: {azure1}")
    print()
    
    # Example 2: DECODE
    print("📝 Example 2: DECODE to CASE")
    print("-" * 80)
    oracle2 = "SELECT DECODE(status, 'A', 'Active', 'I', 'Inactive', 'Unknown') FROM emp"
    print(f"Oracle:    {oracle2}")
    azure2, warnings2 = convert_oracle_select_to_azure(oracle2)
    print(f"Azure SQL: {azure2}")
    print()
    
    # Example 3: Date functions
    print("📝 Example 3: Date Functions")
    print("-" * 80)
    oracle3 = "SELECT * FROM orders WHERE TRUNC(order_date) = TRUNC(SYSDATE)"
    print(f"Oracle:    {oracle3}")
    azure3, warnings3 = convert_oracle_select_to_azure(oracle3)
    print(f"Azure SQL: {azure3}")
    print()
    
    # Example 4: ROWNUM (with warning)
    print("📝 Example 4: ROWNUM with ORDER BY (⚠️ generates warning)")
    print("-" * 80)
    oracle4 = "SELECT * FROM employees WHERE ROWNUM <= 5 ORDER BY salary DESC"
    print(f"Oracle:    {oracle4}")
    azure4, warnings4 = convert_oracle_select_to_azure(oracle4)
    print(f"Azure SQL: {azure4}")
    if warnings4:
        print(f"⚠️  {warnings4[0]}")
    print()
    
    # Example 5: FROM DUAL
    print("📝 Example 5: FROM DUAL Removal")
    print("-" * 80)
    oracle5 = "SELECT SYSDATE, 1+1 AS calc FROM DUAL"
    print(f"Oracle:    {oracle5}")
    azure5, warnings5 = convert_oracle_select_to_azure(oracle5)
    print(f"Azure SQL: {azure5}")
    print()
    
    # Example 6: Complex query
    print("📝 Example 6: Complex Real-World Query")
    print("-" * 80)
    oracle6 = """SELECT 
    emp_id,
    NVL(name, 'N/A') AS name,
    DECODE(dept, 10, 'Sales', 20, 'IT', 'Other') AS department,
    TRUNC(hire_date) AS hired,
    salary
FROM employees
WHERE TRUNC(hire_date) >= TRUNC(SYSDATE) - 365
    AND ROWNUM <= 100"""
    
    print("Oracle:")
    print(oracle6)
    print()
    
    azure6, warnings6 = convert_oracle_select_to_azure(oracle6)
    print("Azure SQL:")
    print(azure6)
    if warnings6:
        print()
        print("Warnings:")
        for w in warnings6:
            print(f"  {w}")
    print()
    
    print("=" * 80)
    print("✅ Demo complete! The tool successfully converted all queries.")
    print("=" * 80)
    print()
    print("💡 TIP: Use 'python -m oracle_to_azure_select_converter -h' for CLI help")
    print()


if __name__ == '__main__':
    demo()
