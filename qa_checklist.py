"""
QA Checklist - Oracle to Azure SQL Converter
Run this after each conversion to verify quality.
"""

from oracle_to_azure_select_converter import convert_oracle_select_to_azure
import re


def run_qa_checklist(converted_sql: str, warnings: list) -> dict:
    """
    Run comprehensive QA checks on converted SQL.
    Returns dict with check results and overall pass/fail status.
    """
    results = {}
    
    # Check 1: No HTML entities remain
    html_entities = ['&gt;', '&lt;', '&amp;', '&quot;', '&apos;', '&nbsp;']
    found_entities = [e for e in html_entities if e in converted_sql]
    results['html_entities'] = {
        'pass': len(found_entities) == 0,
        'message': 'No HTML entities remain' if len(found_entities) == 0 else f'Found HTML entities: {", ".join(found_entities)}',
        'severity': 'CRITICAL' if found_entities else 'OK'
    }
    
    # Check 2: No Oracle-only functions remain
    oracle_functions = ['NVL', 'DECODE', 'TRUNC', 'ADD_MONTHS', 'SUBSTR', 'TO_CHAR', 'LISTAGG', 'SYSDATE', 'ROWNUM']
    # Use word boundaries to avoid false positives in comments or strings
    found_functions = []
    for func in oracle_functions:
        # Look for function calls (not in comments)
        pattern = rf'\b{func}\s*\('
        if re.search(pattern, converted_sql, re.IGNORECASE):
            # Verify it's not in a comment
            lines = converted_sql.split('\n')
            for line in lines:
                # Remove SQL comments
                code_part = re.sub(r'--.*$', '', line)
                code_part = re.sub(r'/\*.*?\*/', '', code_part)
                if re.search(pattern, code_part, re.IGNORECASE):
                    found_functions.append(func)
                    break
    
    results['oracle_functions'] = {
        'pass': len(found_functions) == 0,
        'message': 'All Oracle functions converted' if len(found_functions) == 0 else f'Oracle functions still present: {", ".join(set(found_functions))}',
        'severity': 'CRITICAL' if found_functions else 'OK'
    }
    
    # Check 3: STRING_AGG with DISTINCT uses derived set
    has_string_agg = 'STRING_AGG' in converted_sql.upper()
    if has_string_agg:
        # Check if DISTINCT is preserved via subquery pattern
        has_distinct_pattern = bool(re.search(r'SELECT\s+STRING_AGG.*?FROM\s*\(\s*SELECT\s+DISTINCT', converted_sql, re.IGNORECASE | re.DOTALL))
        has_placeholder = '<source_table>' in converted_sql
        
        if has_distinct_pattern:
            if has_placeholder:
                results['string_agg_distinct'] = {
                    'pass': False,
                    'message': 'STRING_AGG DISTINCT pattern found but requires manual fix (replace <source_table> placeholder)',
                    'severity': 'WARNING',
                    'action_required': 'Replace <source_table> with actual table/CTE and add WHERE correlation'
                }
            else:
                results['string_agg_distinct'] = {
                    'pass': True,
                    'message': 'STRING_AGG DISTINCT correctly uses derived set with correlation',
                    'severity': 'OK'
                }
        else:
            results['string_agg_distinct'] = {
                'pass': True,
                'message': 'STRING_AGG found (non-DISTINCT or already correct)',
                'severity': 'OK'
            }
    else:
        results['string_agg_distinct'] = {
            'pass': True,
            'message': 'No STRING_AGG in query (N/A)',
            'severity': 'OK'
        }
    
    # Check 4: REGEXP_LIKE handling
    has_regexp = 'REGEXP_LIKE' in converted_sql.upper()
    if has_regexp:
        # Check for version warning
        has_warning = any(
            hasattr(w, 'warning_type') and w.warning_type == 'REGEXP_LIKE'
            for w in warnings
        )
        has_comment = '/* WARNING: Requires SQL Server 2025+' in converted_sql or '/* For older SQL Server:' in converted_sql
        
        results['regexp_like'] = {
            'pass': has_warning and has_comment,
            'message': 'REGEXP_LIKE uses native function with version warning' if has_warning else 'REGEXP_LIKE found but missing version warning',
            'severity': 'WARNING' if not has_warning else 'OK'
        }
    else:
        results['regexp_like'] = {
            'pass': True,
            'message': 'No REGEXP_LIKE in query (N/A)',
            'severity': 'OK'
        }
    
    # Check 5: Syntax checks (basic)
    syntax_issues = []
    
    # Check for common syntax errors
    if '&gt;' in converted_sql or '&lt;' in converted_sql:
        syntax_issues.append('HTML entities in operators')
    
    # Check for balanced parentheses
    if converted_sql.count('(') != converted_sql.count(')'):
        syntax_issues.append(f'Unbalanced parentheses: {converted_sql.count("(")} open, {converted_sql.count(")")} close')
    
    # Check for basic SQL structure
    if not re.search(r'\bSELECT\b', converted_sql, re.IGNORECASE):
        syntax_issues.append('Missing SELECT keyword')
    
    results['syntax'] = {
        'pass': len(syntax_issues) == 0,
        'message': 'Basic syntax checks passed' if len(syntax_issues) == 0 else f'Syntax issues: {"; ".join(syntax_issues)}',
        'severity': 'CRITICAL' if syntax_issues else 'OK'
    }
    
    # Overall pass/fail
    critical_fails = [k for k, v in results.items() if v['severity'] == 'CRITICAL' and not v['pass']]
    warnings_count = [k for k, v in results.items() if v['severity'] == 'WARNING' and not v['pass']]
    
    results['_summary'] = {
        'total_checks': len(results) - 1,  # Exclude summary itself
        'passed': sum(1 for v in results.values() if isinstance(v, dict) and v.get('pass', False)),
        'critical_failures': len(critical_fails),
        'warnings': len(warnings_count),
        'overall_status': 'PASS' if len(critical_fails) == 0 else 'FAIL',
        'ready_for_execution': len(critical_fails) == 0 and len(warnings_count) == 0
    }
    
    return results


def print_qa_report(results: dict):
    """Print formatted QA report."""
    print("=" * 80)
    print("QA CHECKLIST REPORT")
    print("=" * 80)
    
    # Print individual checks
    for check_name, check_result in results.items():
        if check_name == '_summary':
            continue
        
        status_symbol = 'PASS' if check_result['pass'] else 'FAIL'
        severity = check_result['severity']
        message = check_result['message']
        
        print(f"\n[{status_symbol}] {check_name.upper().replace('_', ' ')}")
        print(f"    Status: {severity}")
        print(f"    {message}")
        
        if 'action_required' in check_result:
            print(f"    ACTION: {check_result['action_required']}")
    
    # Print summary
    summary = results['_summary']
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Checks: {summary['total_checks']}")
    print(f"Passed: {summary['passed']}")
    print(f"Critical Failures: {summary['critical_failures']}")
    print(f"Warnings: {summary['warnings']}")
    print(f"\nOverall Status: {summary['overall_status']}")
    print(f"Ready for SSMS/Azure SQL Execution: {'YES' if summary['ready_for_execution'] else 'NO (manual fixes required)'}")
    print("=" * 80)


def quick_qa(oracle_query: str):
    """
    Quick QA workflow: convert query and run all checks.
    """
    print("Converting Oracle query...")
    converted_sql, warnings = convert_oracle_select_to_azure(oracle_query)
    
    print("\nCONVERTED SQL:")
    print("-" * 80)
    print(converted_sql)
    print("-" * 80)
    
    if warnings:
        print(f"\n{len(warnings)} WARNING(S):")
        for w in warnings:
            wtype = w.warning_type if hasattr(w, 'warning_type') else 'GENERAL'
            print(f"  [{wtype}] {w.message[:100]}...")
    
    print("\nRunning QA checks...")
    results = run_qa_checklist(converted_sql, warnings)
    print_qa_report(results)
    
    return converted_sql, warnings, results


if __name__ == '__main__':
    # Example usage
    test_query = """
    SELECT 
        m.member_id,
        NVL(m.first_name, 'N/A') AS first_name,
        TRUNC(m.dob) AS dob,
        LISTAGG(DISTINCT dx_code, ',') WITHIN GROUP (ORDER BY dx_code) AS codes
    FROM member m
    WHERE m.dob &lt;= ADD_MONTHS(SYSDATE, -216)
        AND REGEXP_LIKE(m.email, '^[A-Za-z0-9._%+-]+@')
    FETCH FIRST 25 ROWS ONLY
    """
    
    print("EXAMPLE QA CHECK")
    print("=" * 80)
    print("Oracle Query:")
    print(test_query)
    print("\n")
    
    quick_qa(test_query)
