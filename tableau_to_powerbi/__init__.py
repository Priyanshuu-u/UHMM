"""
Tableau to Power BI Converter

A tool for automated conversion of Tableau workbooks (.twbx) to Power BI (.pbix) files.
"""

__version__ = '0.1.0'

from .converter import TableauToPowerBIConverter

__all__ = ['TableauToPowerBIConverter']