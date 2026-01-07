"""Azure SQL to Oracle SELECT Query Converter (Reverse Direction)
"""

import re
from typing import List, Tuple
from .converter import ConversionWarning

# Pre-compile regex patterns for better performance
_TOP_PATTERN = re.compile(r'\bSELECT\s+TOP\s+(\d+)\s+', re.IGNORECASE)
_WHERE_PATTERN = re.compile(r'\bWHERE\b', re.IGNORECASE)
_ORDER_BY_PATTERN_REVERSE = re.compile(r'\bORDER\s+BY\b', re.IGNORECASE)
_GETDATE_PATTERN = re.compile(r'\bGETDATE\s*\(\s*\)', re.IGNORECASE)
_ISNULL_PATTERN = re.compile(r'\bISNULL\s*\(((?:[^()]|\([^()]*\))*)\)', re.IGNORECASE)
_CAST_DATE_PATTERN = re.compile(r'\bCAST\s*\(([^)]+)\s+AS\s+DATE\s*\)', re.IGNORECASE)
_CASE_WHEN_PATTERN = re.compile(r'\bCASE\s+WHEN\b', re.IGNORECASE)


class AzureToOracleConverter:
    """Converts Azure SQL/SQL Server SELECT queries to Oracle format."""
    
    def __init__(self):
        self.warnings: List[ConversionWarning] = []
    
    def convert(self, azure_query: str) -> Tuple[str, List[ConversionWarning]]:
        """
        Convert an Azure SQL SELECT query to Oracle format.
        
        Args:
            azure_query: The Azure SQL SELECT query string
            
        Returns:
            Tuple of (converted_query, list_of_warnings)
        """
        self.warnings = []
        
        # Input validation
        if not azure_query or not isinstance(azure_query, str):
            self.warnings.append(
                ConversionWarning("Invalid input: Query must be a non-empty string.")
            )
            return azure_query if azure_query else "", self.warnings
        
        # Validate it's a SELECT query
        if not self._is_select_query(azure_query):
            self.warnings.append(
                ConversionWarning("Query does not appear to be a SELECT statement.")
            )
            return azure_query, self.warnings
        
        # Apply reverse conversions
        converted = azure_query
        converted = self._convert_top_to_rownum(converted)
        converted = self._convert_getdate(converted)
        converted = self._convert_isnull(converted)
        converted = self._convert_string_concatenation(converted)
        converted = self._convert_cast_date(converted)
        converted = self._convert_case_to_decode(converted)
        
        return converted, self.warnings
    
    def _is_select_query(self, query: str) -> bool:
        """Check if query is a SELECT statement."""
        query_upper = query.strip().upper()
        return query_upper.startswith('SELECT') or query_upper.startswith('WITH')
    
    def _convert_top_to_rownum(self, query: str) -> str:
        """
        Convert SELECT TOP N to WHERE ROWNUM <= N.
        Note: This is a basic conversion. Complex TOP usage may need manual review.
        """
        match = _TOP_PATTERN.search(query)
        
        if not match:
            return query
        
        limit = match.group(1)
        converted = _TOP_PATTERN.sub('SELECT ', query)
        
        # Add WHERE ROWNUM <= N (or extend existing WHERE)
        if _WHERE_PATTERN.search(converted):
            converted = _WHERE_PATTERN.sub(f'WHERE ROWNUM <= {limit} AND', converted, count=1)
        elif _ORDER_BY_PATTERN_REVERSE.search(converted):
            converted = _ORDER_BY_PATTERN_REVERSE.sub(f'WHERE ROWNUM <= {limit} ORDER BY', converted, count=1)
        else:
            converted = converted.rstrip() + f'\nWHERE ROWNUM <= {limit}'
        
        # Warn about ORDER BY
        if _ORDER_BY_PATTERN_REVERSE.search(converted):
            self.warnings.append(
                ConversionWarning("TOP converted to ROWNUM with ORDER BY. Results may differ - consider using a subquery.")
            )
        
        return converted
    
    def _convert_getdate(self, query: str) -> str:
        """Convert GETDATE() to SYSDATE."""
        return _GETDATE_PATTERN.sub('SYSDATE', query)
    
    def _convert_isnull(self, query: str) -> str:
        """Convert ISNULL(a, b) to NVL(a, b)."""
        return _ISNULL_PATTERN.sub(lambda m: f"NVL({m.group(1)})", query)
    
    def _convert_string_concatenation(self, query: str) -> str:
        """
        Convert + to || for string concatenation.
        Note: This is a heuristic and may not be perfect for numeric addition.
        """
        if '+' in query and "'" in query:
            converted = query.replace(' + ', ' || ')
            self.warnings.append(
                ConversionWarning("String concatenation operator (+) converted to (||). Verify numeric additions are not affected.")
            )
            return converted
        return query
    
    def _convert_cast_date(self, query: str) -> str:
        """Convert CAST(date_col AS DATE) to TRUNC(date_col)."""
        return _CAST_DATE_PATTERN.sub(lambda m: f"TRUNC({m.group(1).strip()})", query)
    
    def _convert_case_to_decode(self, query: str) -> str:
        """
        Convert simple CASE WHEN to DECODE.
        Only converts simple equality cases.
        """
        if _CASE_WHEN_PATTERN.search(query):
            self.warnings.append(
                ConversionWarning("CASE WHEN statement found. Consider converting to DECODE manually for better Oracle compatibility.")
            )
        return query


def convert_azure_select_to_oracle(azure_query: str) -> Tuple[str, List[ConversionWarning]]:
    """
    Convert an Azure SQL SELECT query to Oracle format.
    
    Args:
        azure_query: Azure SQL SELECT query string
        
    Returns:
        Tuple of (converted_oracle_query, list_of_warnings)
    """
    converter = AzureToOracleConverter()
    return converter.convert(azure_query)
