"""Debug script to test GUI conversion"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from oracle_to_azure_select_converter import convert_oracle_select_to_azure

# Test query
oracle_query = """SELECT 
    TRUNC(m.effective_date) AS eff_date,
    NVL(m.email, 'noemail@example.com') AS email,
    em.first_name || ' ' || em.last_name AS full_name
FROM member m
WHERE NVL(m.status, 'N') = 'A'"""

print("="*70)
print("TESTING CONVERSION")
print("="*70)
print("\nINPUT (Oracle):")
print(oracle_query)

# Call the converter
azure_query, warnings = convert_oracle_select_to_azure(oracle_query)

print("\n" + "="*70)
print("OUTPUT (Azure):")
print("="*70)
print(azure_query)

print("\n" + "="*70)
print(f"WARNINGS: {len(warnings)}")
print("="*70)

# Verify conversions happened
print("\nVERIFICATION:")
print(f"  TRUNC found in output: {('TRUNC' in azure_query)}")
print(f"  CAST found in output: {('CAST' in azure_query)}")
print(f"  NVL found in output: {('NVL' in azure_query)}")
print(f"  ISNULL found in output: {('ISNULL' in azure_query)}")
print(f"  || found in output: {('||' in azure_query)}")
print(f"  + found in output: {('+' in azure_query)}")

if 'CAST' in azure_query and 'ISNULL' in azure_query and '+' in azure_query:
    print("\n✅ CONVERSION WORKING CORRECTLY!")
else:
    print("\n❌ CONVERSION FAILED - NO CHANGES MADE!")
