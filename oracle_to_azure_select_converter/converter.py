"""
Main converter module for Oracle to Azure SQL SELECT query conversion.
"""

import re
from typing import List, Tuple


class ConversionWarning:
    """Represents a warning generated during conversion."""
    
    def __init__(self, message: str, line_number: int = None):
        self.message = message
        self.line_number = line_number
    
    def __str__(self):
        if self.line_number:
            return f"⚠ WARNING (Line {self.line_number}): {self.message}"
        return f"⚠ WARNING: {self.message}"


class OracleToAzureConverter:
    """Converts Oracle SELECT queries to Azure SQL format."""
    
    def __init__(self):
        self.warnings: List[ConversionWarning] = []
    
    def convert(self, oracle_query: str) -> Tuple[str, List[ConversionWarning]]:
        """
        Convert an Oracle SELECT query to Azure SQL format.
        
        Args:
            oracle_query: The Oracle SQL SELECT query string
            
        Returns:
            Tuple of (converted_query, list_of_warnings)
        """
        self.warnings = []
        
        # Validate it's a SELECT query
        if not self._is_select_query(oracle_query):
            self.warnings.append(
                ConversionWarning("Query does not appear to be a SELECT statement. Only SELECT queries are supported.")
            )
            return oracle_query, self.warnings
        
        # Check for unsupported features first
        self._detect_unsupported_features(oracle_query)
        
        # Apply conversions in order
        converted = oracle_query
        converted = self._convert_nvl(converted)
        converted = self._convert_decode(converted)
        converted = self._convert_sysdate(converted)
        converted = self._convert_string_concatenation(converted)
        converted = self._convert_date_trunc(converted)
        converted = self._remove_from_dual(converted)
        converted = self._convert_rownum_to_top(converted)
        
        return converted, self.warnings
    
    def _is_select_query(self, query: str) -> bool:
        """Check if query is a SELECT statement."""
        query_upper = query.strip().upper()
        return query_upper.startswith('SELECT') or query_upper.startswith('WITH')
    
    def _detect_unsupported_features(self, query: str):
        """Detect features that require manual review."""
        query_upper = query.upper()
        
        # Check for CONNECT BY (hierarchical queries)
        if re.search(r'\bCONNECT\s+BY\b', query_upper):
            self.warnings.append(
                ConversionWarning("CONNECT BY detected. Hierarchical queries require manual conversion using CTEs or recursive queries.")
            )
        
        # Check for ROWNUM with ORDER BY (pagination issue)
        if self._has_rownum_with_order_by(query):
            self.warnings.append(
                ConversionWarning("ROWNUM used with ORDER BY. Manual review required - results may differ. Consider using ROW_NUMBER() OVER(ORDER BY ...) instead.")
            )
        
        # Check for complex date arithmetic
        if re.search(r'\+\s*\d+\s*[/]\s*24', query_upper) or re.search(r'\+\s*INTERVAL', query_upper):
            self.warnings.append(
                ConversionWarning("Complex date arithmetic detected. Verify DATEADD() conversion is semantically correct.")
            )
        
        # Check for correlated subqueries (informational warning)
        if self._has_correlated_subquery(query):
            self.warnings.append(
                ConversionWarning("Possible correlated subquery detected. Verify query logic after conversion.")
            )
    
    def _has_rownum_with_order_by(self, query: str) -> bool:
        """Check if ROWNUM is used together with ORDER BY."""
        query_upper = query.upper()
        has_rownum = re.search(r'\bROWNUM\b', query_upper)
        has_order_by = re.search(r'\bORDER\s+BY\b', query_upper)
        return bool(has_rownum and has_order_by)
    
    def _has_correlated_subquery(self, query: str) -> bool:
        """Detect potential correlated subqueries (basic heuristic)."""
        # Look for subqueries with WHERE clauses referencing outer table
        # This is a simplified check
        subquery_pattern = r'\(\s*SELECT\s+.*?\bWHERE\b.*?\)'
        matches = re.findall(subquery_pattern, query.upper(), re.DOTALL)
        return len(matches) > 0
    
    def _convert_nvl(self, query: str) -> str:
        """
        Convert Oracle NVL(a, b) to SQL Server ISNULL(a, b).
        NVL returns the first non-null argument.
        """
        # Match NVL with nested parentheses support
        def replace_nvl(match):
            content = match.group(1)
            return f"ISNULL({content})"
        
        # Simple pattern for NVL - handles most cases
        pattern = r'\bNVL\s*\(((?:[^()]|\([^()]*\))*)\)'
        converted = re.sub(pattern, replace_nvl, query, flags=re.IGNORECASE)
        
        return converted
    
    def _convert_decode(self, query: str) -> str:
        """
        Convert Oracle DECODE to ANSI CASE WHEN.
        DECODE(expr, search1, result1, search2, result2, ..., default)
        """
        def replace_decode(match):
            content = match.group(1).strip()
            parts = self._split_decode_args(content)
            
            if len(parts) < 3:
                return match.group(0)  # Invalid DECODE, leave as-is
            
            expr = parts[0]
            case_parts = []
            
            # Process pairs
            i = 1
            while i < len(parts) - 1:
                search = parts[i]
                result = parts[i + 1] if i + 1 < len(parts) else None
                if result:
                    case_parts.append(f"WHEN {expr} = {search} THEN {result}")
                i += 2
            
            # Default value (if odd number of arguments after expr)
            default = None
            if len(parts) % 2 == 0:  # Even total means there's a default
                default = parts[-1]
            
            case_stmt = "CASE " + " ".join(case_parts)
            if default:
                case_stmt += f" ELSE {default}"
            case_stmt += " END"
            
            return case_stmt
        
        pattern = r'\bDECODE\s*\(((?:[^()]|\([^()]*\))*)\)'
        converted = re.sub(pattern, replace_decode, query, flags=re.IGNORECASE)
        
        return converted
    
    def _split_decode_args(self, content: str) -> List[str]:
        """Split DECODE arguments respecting nested parentheses and quoted strings."""
        parts = []
        current = []
        depth = 0
        in_quote = False
        quote_char = None
        
        for char in content:
            if char in ("'", '"') and not in_quote:
                in_quote = True
                quote_char = char
                current.append(char)
            elif char == quote_char and in_quote:
                in_quote = False
                quote_char = None
                current.append(char)
            elif char == '(' and not in_quote:
                depth += 1
                current.append(char)
            elif char == ')' and not in_quote:
                depth -= 1
                current.append(char)
            elif char == ',' and depth == 0 and not in_quote:
                parts.append(''.join(current).strip())
                current = []
            else:
                current.append(char)
        
        if current:
            parts.append(''.join(current).strip())
        
        return parts
    
    def _convert_sysdate(self, query: str) -> str:
        """
        Convert Oracle SYSDATE to SQL Server GETDATE().
        SYSDATE returns current date and time.
        """
        # Replace SYSDATE with GETDATE()
        converted = re.sub(r'\bSYSDATE\b', 'GETDATE()', query, flags=re.IGNORECASE)
        return converted
    
    def _convert_string_concatenation(self, query: str) -> str:
        """
        Convert Oracle string concatenation (||) to SQL Server (+).
        Handle cases where || is used between columns/literals.
        """
        # Replace || with + for string concatenation
        # Be careful not to replace || in comments
        converted = re.sub(r'\|\|', '+', query)
        return converted
    
    def _convert_date_trunc(self, query: str) -> str:
        """
        Convert Oracle TRUNC(date_col) to SQL Server CAST(date_col AS DATE).
        TRUNC removes time portion from datetime.
        """
        def replace_trunc(match):
            content = match.group(1).strip()
            return f"CAST({content} AS DATE)"
        
        # Match TRUNC with single argument (date truncation)
        pattern = r'\bTRUNC\s*\(([^,)]+)\)'
        converted = re.sub(pattern, replace_trunc, query, flags=re.IGNORECASE)
        
        return converted
    
    def _remove_from_dual(self, query: str) -> str:
        """
        Remove FROM DUAL clause (Oracle's dummy table).
        In SQL Server, FROM clause is optional for SELECT without tables.
        """
        # Remove FROM DUAL (case-insensitive)
        converted = re.sub(r'\bFROM\s+DUAL\b', '', query, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        converted = re.sub(r'\s+', ' ', converted)
        
        return converted
    
    def _convert_rownum_to_top(self, query: str) -> str:
        """
        Convert WHERE ROWNUM <= N to SELECT TOP N.
        Note: This is a simple conversion. Complex ROWNUM usage needs manual review.
        """
        # Pattern: WHERE ROWNUM <= number or WHERE ROWNUM < number
        rownum_pattern = r'\bWHERE\s+ROWNUM\s*(<=?|<)\s*(\d+)'
        match = re.search(rownum_pattern, query, flags=re.IGNORECASE)
        
        if match:
            operator = match.group(1)
            limit = int(match.group(2))
            
            # Adjust limit for < vs <=
            if operator == '<':
                limit -= 1
            
            # Remove the WHERE ROWNUM clause
            converted = re.sub(rownum_pattern, '', query, flags=re.IGNORECASE)
            
            # Add TOP N after SELECT
            converted = re.sub(
                r'\bSELECT\b',
                f'SELECT TOP {limit}',
                converted,
                count=1,
                flags=re.IGNORECASE
            )
            
            return converted
        
        return query


def convert_oracle_select_to_azure(oracle_query: str) -> Tuple[str, List[ConversionWarning]]:
    """
    Convert an Oracle SELECT query to Azure SQL/SQL Server format.
    
    This is a QA support tool for converting read-only Oracle queries.
    It performs deterministic, safe conversions and warns about complex features.
    
    Args:
        oracle_query: Oracle SQL SELECT query string
        
    Returns:
        Tuple of (converted_azure_query, list_of_warnings)
        
    Example:
        >>> query = "SELECT NVL(name, 'Unknown') FROM employees WHERE ROWNUM <= 10"
        >>> converted, warnings = convert_oracle_select_to_azure(query)
        >>> print(converted)
        SELECT TOP 10 ISNULL(name, 'Unknown') FROM employees
    """
    converter = OracleToAzureConverter()
    return converter.convert(oracle_query)
