#!/usr/bin/env python3
"""
Command-line interface for Oracle to Azure SQL SELECT query converter.
"""

import argparse
import sys
from pathlib import Path
from .converter import convert_oracle_select_to_azure


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Convert Oracle SELECT queries to Azure SQL/SQL Server format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a query from command line
  python -m oracle_to_azure_select_converter -q "SELECT NVL(name, 'N/A') FROM DUAL"
  
  # Convert a query from file
  python -m oracle_to_azure_select_converter -f query.sql
  
  # Save output to file
  python -m oracle_to_azure_select_converter -f input.sql -o output.sql
        """
    )
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '-q', '--query',
        type=str,
        help='Oracle SQL query string to convert'
    )
    input_group.add_argument(
        '-f', '--file',
        type=Path,
        help='Path to file containing Oracle SQL query'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file path (default: print to stdout)'
    )
    
    parser.add_argument(
        '--no-warnings',
        action='store_true',
        help='Suppress warning messages'
    )
    
    args = parser.parse_args()
    
    # Get the query
    if args.query:
        oracle_query = args.query
    else:
        try:
            oracle_query = args.file.read_text(encoding='utf-8')
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return 1
    
    # Convert the query
    converted_query, warnings = convert_oracle_select_to_azure(oracle_query)
    
    # Prepare output
    output_lines = []
    
    # Add warnings if present and not suppressed
    if warnings and not args.no_warnings:
        output_lines.append("=" * 70)
        output_lines.append("CONVERSION WARNINGS")
        output_lines.append("=" * 70)
        for warning in warnings:
            output_lines.append(str(warning))
        output_lines.append("")
    
    # Add converted query
    if warnings and not args.no_warnings:
        output_lines.append("=" * 70)
        output_lines.append("CONVERTED QUERY")
        output_lines.append("=" * 70)
    output_lines.append(converted_query)
    
    output_text = "\n".join(output_lines)
    
    # Write output
    if args.output:
        try:
            args.output.write_text(output_text, encoding='utf-8')
            print(f"Conversion complete. Output written to: {args.output}")
            if warnings and not args.no_warnings:
                print(f"\n{len(warnings)} warning(s) generated. Check output file.")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 1
    else:
        print(output_text)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
