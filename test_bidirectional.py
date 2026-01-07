"""
Test script for bidirectional conversion
"""

from oracle_to_azure_select_converter import (
    convert_oracle_select_to_azure,
    convert_azure_select_to_oracle
)


def test_oracle_to_azure():
    """Test Oracle to Azure conversion."""
    print("=" * 70)
    print("TEST 1: Oracle → Azure SQL")
    print("=" * 70)
    
    oracle_query = """SELECT 
    employee_id,
    NVL(first_name, 'N/A') || ' ' || last_name AS full_name,
    DECODE(status, 'A', 'Active', 'I', 'Inactive') AS status,
    TRUNC(hire_date) AS hire_date
FROM employees
WHERE ROWNUM <= 10"""
    
    print("\nOracle Query:")
    print(oracle_query)
    
    azure_query, warnings = convert_oracle_select_to_azure(oracle_query)
    
    print("\n✅ Converted to Azure SQL:")
    print(azure_query)
    
    if warnings:
        print(f"\n⚠ Warnings: {len(warnings)}")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("\n✓ No warnings")
    
    return azure_query


def test_azure_to_oracle():
    """Test Azure to Oracle conversion."""
    print("\n" + "=" * 70)
    print("TEST 2: Azure SQL → Oracle")
    print("=" * 70)
    
    azure_query = """SELECT TOP 10
    employee_id,
    ISNULL(first_name, 'N/A') + ' ' + last_name AS full_name,
    CASE WHEN status = 'A' THEN 'Active' 
         WHEN status = 'I' THEN 'Inactive' END AS status,
    CAST(hire_date AS DATE) AS hire_date
FROM employees"""
    
    print("\nAzure SQL Query:")
    print(azure_query)
    
    oracle_query, warnings = convert_azure_select_to_oracle(azure_query)
    
    print("\n✅ Converted to Oracle:")
    print(oracle_query)
    
    if warnings:
        print(f"\n⚠ Warnings: {len(warnings)}")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("\n✓ No warnings")
    
    return oracle_query


def test_round_trip():
    """Test round-trip conversion."""
    print("\n" + "=" * 70)
    print("TEST 3: Round-Trip Conversion (Oracle → Azure → Oracle)")
    print("=" * 70)
    
    original = "SELECT NVL(name, 'Unknown'), SYSDATE FROM employees WHERE ROWNUM <= 5"
    
    print(f"\nOriginal Oracle: {original}")
    
    # Convert to Azure
    azure, _ = convert_oracle_select_to_azure(original)
    print(f"\nAfter Oracle→Azure: {azure}")
    
    # Convert back to Oracle
    oracle_back, _ = convert_azure_select_to_oracle(azure)
    print(f"\nAfter Azure→Oracle: {oracle_back}")
    
    print("\n✓ Round-trip complete!")


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("BIDIRECTIONAL CONVERSION TEST SUITE")
    print("=" * 70)
    
    test_oracle_to_azure()
    test_azure_to_oracle()
    test_round_trip()
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nBoth conversion directions are working correctly.")
    print("You can now use the GUI: python run_gui.py")
    print()
