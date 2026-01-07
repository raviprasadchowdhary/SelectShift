"""
Oracle to Azure SQL SELECT Query Converter
A QA support tool for converting Oracle SELECT queries to Azure SQL/SQL Server format.
"""

from .converter import convert_oracle_select_to_azure

__version__ = "1.0.0"
__all__ = ["convert_oracle_select_to_azure"]
