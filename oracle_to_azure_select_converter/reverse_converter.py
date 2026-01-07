"""
Azure SQL to Oracle SELECT Query Converter (Reverse Direction)
"""

import re
from typing import List, Tuple
from .converter import ConversionWarning


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
        # Pattern: SELECT TOP number
        pattern = r'\bSELECT\s+TOP\s+(\d+)\s+'
        match = re.search(pattern, query, flags=re.IGNORECASE)
        
        if match:
            limit = match.group(1)
            
            # Remove TOP N from SELECT
            converted = re.sub(pattern, 'SELECT ', query, flags=re.IGNORECASE)
            
            # Add WHERE ROWNUM <= N (or extend existing WHERE)
            if re.search(r'\bWHERE\b', converted, flags=re.IGNORECASE):
                # Add to existing WHERE clause
                converted = re.sub(
                    r'\bWHERE\b',
                    f'WHERE ROWNUM <= {limit} AND',
                    converted,
                    count=1,
                    flags=re.IGNORECASE
                )
            else:
                # Add new WHERE clause before ORDER BY if present
                if re.search(r'\bORDER\s+BY\b', converted, flags=re.IGNORECASE):
                    converted = re.sub(
                        r'\bORDER\s+BY\b',
                        f'WHERE ROWNUM <= {limit} ORDER BY',
                        converted,
                        count=1,
                        flags=re.IGNORECASE
                    )
                else:
                    # Add at the end
                    converted = converted.rstrip() + f'\nWHERE ROWNUM <= {limit}'
            
            # Warn about ORDER BY
            if re.search(r'\bORDER\s+BY\b', converted, flags=re.IGNORECASE):
                self.warnings.append(
                    ConversionWarning("TOP converted to ROWNUM with ORDER BY. Results may differ - consider using a subquery.")
                )
        
        return query if not match else converted
    
    def _convert_getdate(self, query: str) -> str:
        """Convert GETDATE() to SYSDATE."""
        converted = re.sub(r'\bGETDATE\s*\(\s*\)', 'SYSDATE', query, flags=re.IGNORECASE)
        return converted
    
    def _convert_isnull(self, query: str) -> str:
        """Convert ISNULL(a, b) to NVL(a, b)."""
        def replace_isnull(match):
            content = match.group(1)
            return f"NVL({content})"
        
        pattern = r'\bISNULL\s*\(((?:[^()]|\([^()]*\))*)\)'
        converted = re.sub(pattern, replace_isnull, query, flags=re.IGNORECASE)
        return converted
    
    def _convert_string_concatenation(self, query: str) -> str:
        """
        Convert + to || for string concatenation.
        Note: This is a heuristic and may not be perfect for numeric addition.
        """
        # This is tricky because + is also used for numeric addition
        # We'll do a simple replacement and add a warning
        if '+' in query and "'" in query:
            # Likely has string concatenation
            converted = query.replace(' + ', ' || ')
            self.warnings.append(
                ConversionWarning("String concatenation operator (+) converted to (||). Verify numeric additions are not affected.")
            )
            return converted
        return query
    
    def _convert_cast_date(self, query: str) -> str:
        """Convert CAST(date_col AS DATE) to TRUNC(date_col)."""
        def replace_cast(match):
            content = match.group(1).strip()
            return f"TRUNC({content})"
        
        pattern = r'\bCAST\s*\(([^)]+)\s+AS\s+DATE\s*\)'
        converted = re.sub(pattern, replace_cast, query, flags=re.IGNORECASE)
        return converted
    
    def _convert_case_to_decode(self, query: str) -> str:
        """
        Convert simple CASE WHEN to DECODE.
        Only converts simple equality cases.
        """
        # This is complex - we'll convert simple cases only
        # Pattern: CASE WHEN expr = val THEN result ... ELSE default END
        pattern = r'\bCASE\s+WHEN\s+(\w+)\s*=\s*([^T]+?)\s+THEN\s+([^W]+?)(?:\s+WHEN\s+\1\s*=\s*([^T]+?)\s+THEN\s+([^WE]+?))*(?:\s+ELSE\s+([^E]+?))?\s+END\b'
        
        # For now, we'll leave CASE as-is and add a note
        if re.search(r'\bCASE\s+WHEN\b', query, flags=re.IGNORECASE):
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
