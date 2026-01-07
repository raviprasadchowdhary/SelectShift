"""Main converter module for Oracle to Azure SQL SELECT query conversion.
"""

import re
from typing import List, Tuple

# Pre-compile regex patterns for better performance
_CONNECT_BY_PATTERN = re.compile(r'\bCONNECT\s+BY\b', re.IGNORECASE)
_ROWNUM_PATTERN = re.compile(r'\bROWNUM\b', re.IGNORECASE)
_ORDER_BY_PATTERN = re.compile(r'\bORDER\s+BY\b', re.IGNORECASE)
_DATE_ARITHMETIC_PATTERN = re.compile(r'\+\s*\d+\s*[/]\s*24|\+\s*INTERVAL', re.IGNORECASE)
_SUBQUERY_PATTERN = re.compile(r'\(\s*SELECT\s+.*?\bWHERE\b.*?\)', re.IGNORECASE | re.DOTALL)
_NVL_PATTERN = re.compile(r'\bNVL\s*\(((?:[^()]|\([^()]*\))*)\)', re.IGNORECASE)
_DECODE_PATTERN = re.compile(r'\bDECODE\s*\(((?:[^()]|\([^()]*\))*)\)', re.IGNORECASE)
_SYSDATE_PATTERN = re.compile(r'\bSYSDATE\b', re.IGNORECASE)
_CONCAT_PATTERN = re.compile(r'\|\|')
_TRUNC_PATTERN = re.compile(r'\bTRUNC\s*\(', re.IGNORECASE)
_FROM_DUAL_PATTERN = re.compile(r'\s*\bFROM\s+DUAL\b\s*', re.IGNORECASE)
_ROWNUM_WHERE_PATTERN = re.compile(r'\b(WHERE|AND)\s+ROWNUM\s*(<=?|<)\s*(\d+)', re.IGNORECASE)
_SELECT_PATTERN = re.compile(r'\bSELECT\b', re.IGNORECASE)
_ADD_MONTHS_PATTERN = re.compile(r'\bADD_MONTHS\s*\(', re.IGNORECASE)
_SUBSTR_PATTERN = re.compile(r'\bSUBSTR\s*\(', re.IGNORECASE)
_TO_CHAR_PATTERN = re.compile(r'\bTO_CHAR\s*\(', re.IGNORECASE)
_FETCH_FIRST_PATTERN = re.compile(r'\bFETCH\s+FIRST\s+(\d+)\s+ROWS?\s+ONLY', re.IGNORECASE)
_LISTAGG_PATTERN = re.compile(r'\bLISTAGG\s*\(((?:DISTINCT\s+)?[^,)]+),\s*\'([^\']+)\'\)(?:\s+WITHIN\s+GROUP\s*\(\s*ORDER\s+BY\s+([^)]+)\))?', re.IGNORECASE)
_REGEXP_LIKE_PATTERN = re.compile(r'\bREGEXP_LIKE\s*\(([^,]+),\s*\'([^\']+)\'(?:,\s*\'([^\']+)\')?\)', re.IGNORECASE)
_OPTIMIZER_HINTS_PATTERN = re.compile(r'/\*\+[^*]*\*/', re.IGNORECASE)
_USING_CLAUSE_PATTERN = re.compile(r'\bUSING\s*\(([^)]+)\)', re.IGNORECASE)
_DATE_LITERAL_PATTERN = re.compile(r'\bDATE\s+\'([^\']+)\'', re.IGNORECASE)
_FETCH_WITH_TIES_PATTERN = re.compile(r'\bFETCH\s+FIRST\s+(\d+)\s+ROWS?\s+WITH\s+TIES', re.IGNORECASE)
_MONTHS_BETWEEN_PATTERN = re.compile(r'\bMONTHS_BETWEEN\s*\(([^,]+),\s*([^)]+)\)', re.IGNORECASE)
_REGEXP_SUBSTR_PATTERN = re.compile(r'\bREGEXP_SUBSTR\s*\(', re.IGNORECASE)
_PIVOT_PATTERN = re.compile(r'\bPIVOT\s*\(', re.IGNORECASE)
_LENGTH_PATTERN = re.compile(r'\bLENGTH\s*\(', re.IGNORECASE)
_INSTR_PATTERN = re.compile(r'\bINSTR\s*\(([^,]+),\s*([^)]+)\)', re.IGNORECASE)
_CEIL_PATTERN = re.compile(r'\bCEIL\s*\(', re.IGNORECASE)
_INITCAP_PATTERN = re.compile(r'\bINITCAP\s*\(([^)]+)\)', re.IGNORECASE)
_TRIM_PATTERN = re.compile(r'\bTRIM\s*\(([^()]+(?:\([^()]*\))*)\)', re.IGNORECASE)
_KEEP_DENSE_RANK_PATTERN = re.compile(r'\bKEEP\s*\(\s*DENSE_RANK\s+(FIRST|LAST)', re.IGNORECASE)
_TUPLE_IN_PATTERN = re.compile(r'\([^)]+,\s*[^)]+\)\s+IN\s*\(', re.IGNORECASE)


class ConversionWarning:
    """Represents a warning generated during conversion."""
    
    def __init__(self, message: str, line_number: int = None, warning_type: str = 'GENERAL'):
        self.message = message
        self.line_number = line_number
        self.warning_type = warning_type
    
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
        
        # Input validation
        if not oracle_query or not isinstance(oracle_query, str):
            self.warnings.append(
                ConversionWarning("Invalid input: Query must be a non-empty string.")
            )
            return oracle_query if oracle_query else "", self.warnings
        
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
        converted = self._decode_html_entities(converted)
        converted = self._remove_optimizer_hints(converted)
        converted = self._convert_date_literals(converted)
        converted = self._convert_using_clause(converted)
        converted = self._convert_months_between(converted)
        converted = self._convert_fetch_with_ties(converted)
        converted = self._convert_length(converted)
        converted = self._convert_instr(converted)
        converted = self._convert_ceil(converted)
        converted = self._convert_trim(converted)
        converted = self._convert_initcap(converted)
        converted = self._convert_listagg(converted)
        converted = self._convert_regexp_like(converted)
        converted = self._convert_nvl(converted)
        converted = self._convert_decode(converted)
        converted = self._convert_sysdate(converted)
        converted = self._convert_string_concatenation(converted)
        converted = self._convert_date_trunc(converted)
        converted = self._convert_substr(converted)
        converted = self._convert_to_char(converted)
        converted = self._convert_add_months(converted)
        converted = self._remove_from_dual(converted)
        converted = self._convert_rownum_to_top(converted)
        converted = self._convert_fetch_first(converted)
        
        return converted, self.warnings
    
    def _decode_html_entities(self, query: str) -> str:
        """
        Decode HTML entities like &gt;, &lt;, &amp; to their actual characters.
        Must be done FIRST before any pattern matching.
        """
        query = query.replace('&gt;', '>')
        query = query.replace('&lt;', '<')
        query = query.replace('&amp;', '&')
        query = query.replace('&quot;', '"')
        query = query.replace('&apos;', "'")
        return query
    
    def _convert_listagg(self, query: str) -> str:
        """
        Convert Oracle LISTAGG to SQL Server STRING_AGG.
        Pattern: LISTAGG([DISTINCT] column, 'delimiter') [WITHIN GROUP (ORDER BY column)]
        
        DISTINCT handling: Oracle's LISTAGG(DISTINCT col) must use a subquery approach
        to preserve distinct semantics in SQL Server.
        """
        def replace_listagg(match):
            distinct_col = match.group(1).strip()  # May include DISTINCT
            delimiter = match.group(2)
            order_by = match.group(3)  # May be None
            
            # Check if DISTINCT is used
            has_distinct = 'DISTINCT' in distinct_col.upper()
            if has_distinct:
                # Extract column name after DISTINCT
                col_name = re.sub(r'\bDISTINCT\s+', '', distinct_col, flags=re.IGNORECASE).strip()
                
                # Extract just the column name without table alias for the subquery
                # If col_name is like 'rc.dx3', extract just 'dx3'
                col_parts = col_name.split('.')
                base_col = col_parts[-1] if '.' in col_name else col_name
                
                # Generate subquery pattern to preserve DISTINCT semantics
                # Pattern: (SELECT STRING_AGG(x.col, ',') FROM (SELECT DISTINCT col FROM ...) AS x)
                # Note: This is a placeholder - user needs to adapt it to their query context
                
                if order_by:
                    # With WITHIN GROUP ordering - extract base order column too
                    order_parts = order_by.split('.')
                    base_order = order_parts[-1] if '.' in order_by else order_by
                    
                    result = (
                        f"/* LISTAGG(DISTINCT {col_name}, '{delimiter}') WITHIN GROUP (ORDER BY {order_by}) */\n"
                        f"        (SELECT STRING_AGG(x.{base_col}, '{delimiter}') WITHIN GROUP (ORDER BY x.{base_order})\n"
                        f"         FROM (SELECT DISTINCT {col_name} FROM <source_table>) AS x)"
                    )
                else:
                    result = (
                        f"/* LISTAGG(DISTINCT {col_name}, '{delimiter}') */\n"
                        f"        (SELECT STRING_AGG(x.{base_col}, '{delimiter}')\n"
                        f"         FROM (SELECT DISTINCT {col_name} FROM <source_table>) AS x)"
                    )
                
                self.warnings.append(
                    ConversionWarning(
                        f'LISTAGG(DISTINCT {col_name}) converted to correlated subquery pattern. '
                        f"MANUAL FIX REQUIRED: Replace <source_table> with actual table/CTE name and add WHERE correlation. "
                        f"Example for grouped query: (SELECT STRING_AGG(x.dx3, ',') FROM (SELECT DISTINCT rc2.dx3 FROM recent_claims AS rc2 WHERE rc2.member_id = rc.member_id) AS x)",
                        warning_type='LISTAGG_DISTINCT'
                    )
                )
            else:
                column = distinct_col
                # Build STRING_AGG without DISTINCT
                if order_by:
                    result = f"STRING_AGG({column}, '{delimiter}') WITHIN GROUP (ORDER BY {order_by})"
                else:
                    result = f"STRING_AGG({column}, '{delimiter}')"
            
            return result
        
        return _LISTAGG_PATTERN.sub(replace_listagg, query)
    
    def _convert_regexp_like(self, query: str) -> str:
        """
        Convert Oracle REGEXP_LIKE to SQL Server alternatives.
        Oracle: REGEXP_LIKE(column, 'pattern', 'flags')
        
        SQL Server 2025 (17.x) / Azure SQL with compatibility level >= 170:
        - Native REGEXP_LIKE is available and can be used directly
        
        Older SQL Server versions:
        - Use LIKE for simple patterns
        - Use PATINDEX for slightly more complex patterns
        - Warn about limitations
        """
        def replace_regexp_like(match):
            column = match.group(1).strip()
            pattern = match.group(2)
            flags = match.group(3) if match.group(3) else ''
            
            # For SQL Server 2025+ / Azure SQL compat >= 170, use native REGEXP_LIKE
            # Add a comment to indicate version requirement
            native_regexp = f"REGEXP_LIKE({column}, '{pattern}'{', ' + repr(flags) if flags else ''})"
            
            # Add warning about version requirements
            self.warnings.append(
                ConversionWarning(
                    f"REGEXP_LIKE({column}, '{pattern}') detected. "
                    f'SQL Server 2025 (17.x) / Azure SQL with compatibility level >= 170 supports native REGEXP_LIKE. '
                    f'For older versions, replace with LIKE pattern or PATINDEX. '
                    f'Current conversion uses native REGEXP_LIKE - ensure your SQL Server version supports it.',
                    warning_type='REGEXP_LIKE'
                )
            )
            
            # Try to provide a LIKE alternative as a comment for older versions
            like_alternative = None
            
            # Simple pattern conversions
            if pattern == '^[A-Z]':
                like_alternative = f"{column} LIKE '[A-Z]%' COLLATE Latin1_General_CS_AS"
            elif pattern == '^[a-z]':
                like_alternative = f"{column} LIKE '[a-z]%' COLLATE Latin1_General_CS_AS"
            elif pattern == '^[0-9]' or pattern == '^\\d':
                like_alternative = f"{column} LIKE '[0-9]%'"
            elif pattern.startswith('^') and not any(c in pattern[1:] for c in ['|', '[', '(', '+', '*', '?', '$', '.', '\\']):
                like_alternative = f"{column} LIKE '{pattern[1:]}%'"
            elif pattern.endswith('$') and not any(c in pattern[:-1] for c in ['|', '[', '(', '+', '*', '?', '^', '.', '\\']):
                like_alternative = f"{column} LIKE '%{pattern[:-1]}'"
            elif pattern == '.*':
                like_alternative = f"{column} IS NOT NULL"
            
            # Return native REGEXP_LIKE with optional LIKE alternative as comment
            if like_alternative:
                return f"{native_regexp}  /* For older SQL Server: {like_alternative} */"
            else:
                return f"{native_regexp}  /* WARNING: Requires SQL Server 2025+ or Azure SQL compat >= 170 */"
        
        return _REGEXP_LIKE_PATTERN.sub(replace_regexp_like, query)
    
    def _is_select_query(self, query: str) -> bool:
        """Check if query is a SELECT statement."""
        # Remove comments before checking
        query_cleaned = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)  # Remove /* */ comments
        query_cleaned = re.sub(r'--.*?$', '', query_cleaned, flags=re.MULTILINE)  # Remove -- comments
        query_upper = query_cleaned.strip().upper()
        return query_upper.startswith('SELECT') or query_upper.startswith('WITH')
    
    def _detect_unsupported_features(self, query: str):
        """Detect features that require manual review."""
        # Check for CONNECT BY (hierarchical queries)
        if _CONNECT_BY_PATTERN.search(query):
            self.warnings.append(
                ConversionWarning(
                    "CONNECT BY hierarchical query detected. SQL Server requires recursive CTE with anchor + recursive member using UNION ALL.",
                    warning_type='CONNECT_BY'
                )
            )
        
        # Check for ROWNUM with ORDER BY (pagination issue)
        if self._has_rownum_with_order_by(query):
            self.warnings.append(
                ConversionWarning(
                    "ROWNUM used with ORDER BY. Results may differ - consider ROW_NUMBER() OVER(ORDER BY ...) instead.",
                    warning_type='ROWNUM_ORDER_BY'
                )
            )
        
        # Check for complex date arithmetic
        if _DATE_ARITHMETIC_PATTERN.search(query):
            self.warnings.append(
                ConversionWarning(
                    "Complex date arithmetic detected. Verify DATEADD() conversion is semantically correct.",
                    warning_type='DATE_ARITHMETIC'
                )
            )
        
        # Check for correlated subqueries (informational warning)
        if self._has_correlated_subquery(query):
            self.warnings.append(
                ConversionWarning(
                    "Possible correlated subquery detected. Verify query logic after conversion.",
                    warning_type='CORRELATED_SUBQUERY'
                )
            )
        
        # Check for Oracle PIVOT syntax
        if _PIVOT_PATTERN.search(query):
            self.warnings.append(
                ConversionWarning(
                    "Oracle PIVOT syntax detected. SQL Server PIVOT uses different syntax. Consider conditional aggregation instead.",
                    warning_type='PIVOT'
                )
            )
        
        # Check for KEEP/DENSE_RANK (Oracle analytic)
        if _KEEP_DENSE_RANK_PATTERN.search(query):
            self.warnings.append(
                ConversionWarning(
                    "Oracle KEEP (DENSE_RANK FIRST/LAST) detected. SQL Server requires ROW_NUMBER() with partitioning instead. Manual rewrite needed.",
                    warning_type='KEEP_DENSE_RANK'
                )
            )
        
        # Check for tuple IN comparisons
        if _TUPLE_IN_PATTERN.search(query):
            self.warnings.append(
                ConversionWarning(
                    "Tuple comparison in IN clause detected: (col1, col2) IN (...). SQL Server doesn't support this. Rewrite as: EXISTS (SELECT 1 FROM ... WHERE col1=... AND col2=...)",
                    warning_type='TUPLE_IN'
                )
            )
        
        # Check for REGEXP_SUBSTR
        if _REGEXP_SUBSTR_PATTERN.search(query):
            self.warnings.append(
                ConversionWarning(
                    "REGEXP_SUBSTR detected. SQL Server 2025+ supports this natively; older versions need SUBSTRING+CHARINDEX fallback.",
                    warning_type='REGEXP_SUBSTR'
                )
            )
        
        # LISTAGG and REGEXP_LIKE are now converted automatically
        # Warnings are generated during conversion if needed
    
    def _has_rownum_with_order_by(self, query: str) -> bool:
        """Check if ROWNUM is used together with ORDER BY."""
        return bool(_ROWNUM_PATTERN.search(query) and _ORDER_BY_PATTERN.search(query))
    
    def _has_correlated_subquery(self, query: str) -> bool:
        """Detect potential correlated subqueries (basic heuristic)."""
        return bool(_SUBQUERY_PATTERN.search(query))
    
    def _convert_nvl(self, query: str) -> str:
        """
        Convert Oracle NVL(a, b) to SQL Server ISNULL(a, b).
        NVL returns the first non-null argument.
        Handles nested NVL by applying recursively.
        """
        # Apply pattern multiple times to handle nested NVL
        prev = None
        while prev != query:
            prev = query
            query = _NVL_PATTERN.sub(lambda m: f"ISNULL({m.group(1)})", query)
        return query
    
    def _convert_decode(self, query: str) -> str:
        """
        Convert Oracle DECODE to ANSI CASE WHEN.
        DECODE(expr, search1, result1, search2, result2, ..., default)
        """
        def replace_decode(match):
            parts = self._split_decode_args(match.group(1).strip())
            
            if len(parts) < 3:
                return match.group(0)  # Invalid DECODE, leave as-is
            
            expr = parts[0]
            case_parts = []
            
            # Process pairs
            for i in range(1, len(parts) - 1, 2):
                if i + 1 < len(parts):
                    case_parts.append(f"WHEN {expr} = {parts[i]} THEN {parts[i + 1]}")
            
            # Build CASE statement
            case_stmt = "CASE " + " ".join(case_parts)
            if len(parts) % 2 == 0:  # Even total means there's a default
                case_stmt += f" ELSE {parts[-1]}"
            case_stmt += " END"
            
            return case_stmt
        
        return _DECODE_PATTERN.sub(replace_decode, query)
    
    def _split_function_args(self, content: str) -> List[str]:
        """Split function arguments respecting nested parentheses and quotes."""
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
        return _SYSDATE_PATTERN.sub('GETDATE()', query)
    
    def _convert_string_concatenation(self, query: str) -> str:
        """
        Convert Oracle string concatenation (||) to SQL Server (+).
        Handle cases where || is used between columns/literals.
        """
        return _CONCAT_PATTERN.sub('+', query)
    
    def _convert_substr(self, query: str) -> str:
        """
        Convert Oracle SUBSTR to SQL Server SUBSTRING.
        Both have same syntax: SUBSTR/SUBSTRING(string, start, length)
        """
        return _SUBSTR_PATTERN.sub('SUBSTRING(', query)
    
    def _convert_to_char(self, query: str) -> str:
        """
        Convert Oracle TO_CHAR(date, format) to SQL Server CONVERT.
        Common format 'YYYY-MM-DD' maps to style 120 (ISO format without time).
        """
        result = query
        while True:
            match = _TO_CHAR_PATTERN.search(result)
            if not match:
                break
            
            # Find matching closing paren
            paren_start = match.end() - 1
            depth = 1
            pos = paren_start + 1
            
            while pos < len(result) and depth > 0:
                if result[pos] == '(':
                    depth += 1
                elif result[pos] == ')':
                    depth -= 1
                pos += 1
            
            if depth == 0:
                # Extract the content between parentheses
                content = result[paren_start + 1:pos - 1].strip()
                parts = self._split_function_args(content)
                
                if len(parts) >= 2:
                    date_expr = parts[0].strip()
                    format_str = parts[1].strip().strip("'")
                    
                    # Map common Oracle date formats to SQL Server styles
                    if format_str.upper() in ('YYYY-MM-DD', 'YYYY-MM-DD HH24:MI:SS'):
                        # Style 120: yyyy-mm-dd hh:mi:ss (or just date part with VARCHAR(10))
                        replacement = f"CONVERT(VARCHAR(10), {date_expr}, 120)"
                    else:
                        # Generic conversion - may need manual adjustment
                        replacement = f"FORMAT({date_expr}, '{format_str}')"
                    
                    # Replace the entire TO_CHAR(...) call
                    result = result[:match.start()] + replacement + result[pos:]
                else:
                    # Can't parse, skip this occurrence
                    break
            else:
                # Couldn't find matching paren, skip
                break
        
        return result
    
    def _convert_add_months(self, query: str) -> str:
        """
        Convert Oracle ADD_MONTHS(date, n) to SQL Server DATEADD(MONTH, n, date).
        Also handles special cases like -12 * 18 for years.
        """
        result = query
        while True:
            match = _ADD_MONTHS_PATTERN.search(result)
            if not match:
                break
            
            # Find matching closing paren
            paren_start = match.end() - 1
            depth = 1
            pos = paren_start + 1
            
            while pos < len(result) and depth > 0:
                if result[pos] == '(':
                    depth += 1
                elif result[pos] == ')':
                    depth -= 1
                pos += 1
            
            if depth == 0:
                # Extract the content between parentheses
                content = result[paren_start + 1:pos - 1].strip()
                parts = self._split_function_args(content)
                
                if len(parts) == 2:
                    date_expr = parts[0].strip()
                    months_expr = parts[1].strip()
                    
                    # Check if it's a multiple of 12 (years)
                    # Pattern: -12 * n or n * -12
                    year_match = re.match(r'-12\s*\*\s*(\d+)|(\d+)\s*\*\s*-12', months_expr)
                    if year_match:
                        years = year_match.group(1) or year_match.group(2)
                        replacement = f"DATEADD(YEAR, -{years}, {date_expr})"
                    else:
                        replacement = f"DATEADD(MONTH, {months_expr}, {date_expr})"
                    
                    # Replace the entire ADD_MONTHS(...) call
                    result = result[:match.start()] + replacement + result[pos:]
                else:
                    # Can't parse, skip this occurrence
                    break
            else:
                # Couldn't find matching paren, skip
                break
        
        return result
    
    def _convert_date_trunc(self, query: str) -> str:
        """
        Convert Oracle TRUNC(date_col) to SQL Server CAST(date_col AS DATE).
        TRUNC removes time portion from datetime.
        Handles nested function calls like TRUNC(GETDATE()).
        """
        # Process from right to left to handle nested TRUNC calls
        while True:
            match = _TRUNC_PATTERN.search(query)
            if not match:
                break
            
            # Find the matching closing paren for TRUNC(
            start = match.start()
            paren_start = match.end() - 1  # Position of opening (
            depth = 1
            pos = paren_start + 1
            
            while pos < len(query) and depth > 0:
                if query[pos] == '(':
                    depth += 1
                elif query[pos] == ')':
                    depth -= 1
                pos += 1
            
            if depth == 0:
                # Extract the content between TRUNC( and matching )
                content = query[paren_start + 1:pos - 1].strip()
                replacement = f"CAST({content} AS DATE)"
                query = query[:start] + replacement + query[pos:]
            else:
                # Malformed - skip this match
                break
        
        return query
    
    def _remove_from_dual(self, query: str) -> str:
        """
        Remove FROM DUAL clause (Oracle's dummy table).
        In SQL Server, FROM clause is optional for SELECT without tables.
        """
        # Remove FROM DUAL but preserve general formatting
        converted = _FROM_DUAL_PATTERN.sub(' ', query)
        # Only collapse multiple spaces to single space (not newlines)
        return re.sub(r' {2,}', ' ', converted)
    
    def _convert_rownum_to_top(self, query: str) -> str:
        """
        Convert WHERE ROWNUM <= N or AND ROWNUM <= N to SELECT TOP N.
        Note: This is a simple conversion. Complex ROWNUM usage needs manual review.
        """
        match = _ROWNUM_WHERE_PATTERN.search(query)
        
        if match:
            keyword, operator, limit_str = match.groups()
            limit = int(limit_str) - 1 if operator == '<' else int(limit_str)
            
            # Remove the ROWNUM clause
            converted = _ROWNUM_WHERE_PATTERN.sub('', query)
            
            # Clean up any double spaces or orphaned AND/WHERE
            converted = re.sub(r'\bWHERE\s+AND\b', 'WHERE', converted, flags=re.IGNORECASE)
            converted = re.sub(r'\bAND\s+AND\b', 'AND', converted, flags=re.IGNORECASE)
            converted = re.sub(r' {2,}', ' ', converted)
            
            # Add TOP N after SELECT
            converted = _SELECT_PATTERN.sub(f'SELECT TOP {limit}', converted, count=1)
            return converted
        
        return query
    
    def _convert_fetch_first(self, query: str) -> str:
        """
        Convert Oracle FETCH FIRST n ROWS ONLY to Azure SQL OFFSET 0 ROWS FETCH NEXT n ROWS ONLY.
        Azure SQL requires OFFSET before FETCH.
        """
        def replace_fetch(match):
            n = match.group(1)
            return f'OFFSET 0 ROWS FETCH NEXT {n} ROWS ONLY'
        
        return _FETCH_FIRST_PATTERN.sub(replace_fetch, query)
    
    def _remove_optimizer_hints(self, query: str) -> str:
        """
        Remove Oracle optimizer hints (/*+ ... */) and add a warning.
        Azure SQL doesn't support Oracle optimizer hints.
        """
        if _OPTIMIZER_HINTS_PATTERN.search(query):
            self.warnings.append(ConversionWarning(
                'Oracle optimizer hints (/*+ ... */) have been removed. Azure SQL uses query hints with different syntax. Review execution plans.',
                warning_type='OPTIMIZER_HINTS'
            ))
            return _OPTIMIZER_HINTS_PATTERN.sub(' ', query)
        
        return query
    
    def _convert_using_clause(self, query: str) -> str:
        """
        Convert Oracle USING clause to SQL Server ON clause.
        Oracle: LEFT JOIN table t USING (column_name)
        SQL Server: LEFT JOIN table t ON t.column_name = outer.column_name
        
        Note: This is a best-effort conversion. Manual review required for complex cases.
        """
        if not _USING_CLAUSE_PATTERN.search(query):
            return query
        
        self.warnings.append(ConversionWarning(
            'USING clause detected. Converted to ON clause - verify table aliases are correct.',
            warning_type='USING_CLAUSE'
        ))
        
        # Simple conversion: USING (col) -> ON alias.col = outer_alias.col
        # Note: This requires context to determine correct aliases, so we provide a pattern
        def replace_using(match):
            column = match.group(1).strip()
            # We can't reliably determine the table aliases from regex alone
            # So we convert to a placeholder that user must complete
            return f"ON {column} /* TODO: Add table aliases - e.g., ON t.{column} = outer.{column} */"
        
        return _USING_CLAUSE_PATTERN.sub(replace_using, query)
    
    def _convert_date_literals(self, query: str) -> str:
        """
        Convert Oracle DATE 'YYYY-MM-DD' literals to SQL Server format.
        Oracle: DATE '2025-01-01'
        SQL Server: '2025-01-01' (implicit conversion) or CAST('2025-01-01' AS DATE)
        """
        def replace_date_literal(match):
            date_value = match.group(1)
            # Use explicit CAST for clarity
            return f"'{date_value}'"
        
        return _DATE_LITERAL_PATTERN.sub(replace_date_literal, query)
    
    def _convert_fetch_with_ties(self, query: str) -> str:
        """
        Convert Oracle FETCH FIRST n ROWS WITH TIES to SQL Server TOP (n) WITH TIES.
        Oracle: FETCH FIRST 50 ROWS WITH TIES
        SQL Server: TOP (50) WITH TIES (in SELECT clause)
        
        Note: This requires moving the clause from end to SELECT - flagged for manual review.
        """
        if _FETCH_WITH_TIES_PATTERN.search(query):
            self.warnings.append(ConversionWarning(
                'FETCH FIRST n ROWS WITH TIES detected. In SQL Server, use TOP (n) WITH TIES in the SELECT clause instead. '
                'OFFSET/FETCH does not support WITH TIES in SQL Server.',
                warning_type='FETCH_WITH_TIES'
            ))
            
            # Remove the FETCH clause and suggest TOP usage
            def replace_fetch_ties(match):
                n = match.group(1)
                return f"-- FETCH FIRST {n} ROWS WITH TIES: Use SELECT TOP ({n}) WITH TIES instead"
            
            return _FETCH_WITH_TIES_PATTERN.sub(replace_fetch_ties, query)
        
        return query
    
    def _convert_length(self, query: str) -> str:
        """
        Convert Oracle LENGTH() to SQL Server LEN().
        Oracle: LENGTH(string)
        SQL Server: LEN(string)
        
        Note: Behavior is nearly identical.
        """
        return _LENGTH_PATTERN.sub('LEN(', query)
    
    def _convert_instr(self, query: str) -> str:
        """
        Convert Oracle INSTR to SQL Server CHARINDEX.
        Oracle: INSTR(string, substring) - returns position of substring in string
        SQL Server: CHARINDEX(substring, string) - parameters are reversed!
        
        Note: INSTR returns 0 if not found; CHARINDEX also returns 0 if not found.
        """
        def replace_instr(match):
            string_expr = match.group(1).strip()
            substring_expr = match.group(2).strip()
            # Reverse the parameter order for CHARINDEX
            return f"CHARINDEX({substring_expr}, {string_expr})"
        
        return _INSTR_PATTERN.sub(replace_instr, query)
    
    def _convert_ceil(self, query: str) -> str:
        """
        Convert Oracle CEIL() to SQL Server CEILING().
        Oracle: CEIL(number)
        SQL Server: CEILING(number)
        
        Functionality is identical.
        """
        return _CEIL_PATTERN.sub('CEILING(', query)
    
    def _convert_initcap(self, query: str) -> str:
        """
        Convert Oracle INITCAP() to a TitleCase approximation.
        Oracle: INITCAP(string) - capitalizes first letter of each word
        SQL Server: No native function - use UPPER(LEFT(col,1)) + LOWER(SUBSTRING(col,2,LEN(col)))
        
        Note: This approximation only handles single words. Multi-word strings need custom UDF.
        """
        if _INITCAP_PATTERN.search(query):
            self.warnings.append(ConversionWarning(
                'INITCAP converted to single-word approximation: UPPER(LEFT(col,1)) + LOWER(SUBSTRING(col,2,LEN(col))). '
                'For multi-word strings ("john doe" → "John Doe"), create a custom scalar UDF or use CLR function.',
                warning_type='INITCAP'
            ))
            
            def replace_initcap(match):
                arg = match.group(1).strip()
                # Generate single-word TitleCase approximation
                return f"UPPER(LEFT({arg},1)) + LOWER(SUBSTRING({arg},2,LEN({arg})))"
            
            return _INITCAP_PATTERN.sub(replace_initcap, query)
        
        return query
    
    def _convert_trim(self, query: str) -> str:
        """
        Convert Oracle TRIM() to SQL Server LTRIM(RTRIM()) for maximum compatibility.
        Oracle: TRIM(string)
        SQL Server: TRIM() works in 2017+, but LTRIM(RTRIM()) works in all versions
        """
        if _TRIM_PATTERN.search(query):
            self.warnings.append(ConversionWarning(
                'TRIM() converted to LTRIM(RTRIM(...)) for broad compatibility (SQL Server 2016 and earlier).',
                warning_type='TRIM'
            ))
            
            def replace_trim(match):
                arg = match.group(1).strip()
                return f"LTRIM(RTRIM({arg}))"
            
            return _TRIM_PATTERN.sub(replace_trim, query)
        
        return query
    
    def _convert_months_between(self, query: str) -> str:
        """
        Convert Oracle MONTHS_BETWEEN to SQL Server DATEDIFF.
        Oracle: MONTHS_BETWEEN(date1, date2) returns fractional months
        SQL Server: DATEDIFF(MONTH, date2, date1) returns integer months
        
        Note: Behavior differs - Oracle returns fractional, SQL Server returns integer.
        """
        if _MONTHS_BETWEEN_PATTERN.search(query):
            self.warnings.append(ConversionWarning(
                'MONTHS_BETWEEN converted to DATEDIFF(MONTH, ...). '
                'Note: Oracle returns fractional months, SQL Server returns integer months. '
                'Results may differ if fractional precision is required.',
                warning_type='MONTHS_BETWEEN'
            ))
            
            def replace_months_between(match):
                date1 = match.group(1).strip()
                date2 = match.group(2).strip()
                # SQL Server DATEDIFF has reversed parameter order
                return f"DATEDIFF(MONTH, {date2}, {date1})"
            
            return _MONTHS_BETWEEN_PATTERN.sub(replace_months_between, query)
        
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
