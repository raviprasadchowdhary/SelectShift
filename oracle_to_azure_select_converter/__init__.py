"""
Oracle to Azure SQL SELECT Query Converter
A QA support tool for converting Oracle SELECT queries to Azure SQL/SQL Server format.
Supports bidirectional conversion with GUI interface.
"""

from .converter import convert_oracle_select_to_azure
from .reverse_converter import convert_azure_select_to_oracle

__version__ = "2.0.0"
__all__ = ["convert_oracle_select_to_azure", "convert_azure_select_to_oracle"]
