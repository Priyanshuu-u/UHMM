import logging
import re

logger = logging.getLogger(__name__)

class DaxTranslator:
    """
    Translates Tableau calculated fields to Power BI DAX expressions
    """
    
    def __init__(self):
        # Define mapping from Tableau functions to DAX functions
        self.function_mapping = {
            # Aggregation functions
            'SUM': 'SUM',
            'AVG': 'AVERAGE',
            'MIN': 'MIN',
            'MAX': 'MAX',
            'COUNT': 'COUNT',
            'COUNTD': 'DISTINCTCOUNT',
            
            # Date functions
            'DATEADD': 'DATEADD',
            'DATEDIFF': 'DATEDIFF',
            'DATENAME': 'FORMAT',
            'DATEPART': 'YEAR', # Will be context-dependent
            'DATETRUNC': 'STARTOFMONTH', # Will be context-dependent
            'TODAY': 'TODAY',
            'NOW': 'NOW',
            
            # String functions
            'LEFT': 'LEFT',
            'RIGHT': 'RIGHT',
            'MID': 'MID',
            'LEN': 'LEN',
            'FIND': 'FIND',
            'CONTAINS': 'SEARCH',
            'TRIM': 'TRIM',
            'UPPER': 'UPPER',
            'LOWER': 'LOWER',
            'REPLACE': 'SUBSTITUTE',
            
            # Logical functions
            'IF': 'IF',
            'IFNULL': 'IFERROR',
            'ISNULL': 'ISBLANK',
            'ZN': 'COALESCE',
            
            # Math functions
            'ABS': 'ABS',
            'ROUND': 'ROUND',
            'SQRT': 'SQRT',
            'LOG': 'LN',
            'EXP': 'EXP',
            'POWER': 'POWER',
        }
    
    def translate_calculations(self, calculations):
        """
        Translate a list of Tableau calculations to DAX measures
        
        Args:
            calculations: List of dictionaries with calculation information
            
        Returns:
            List of dictionaries with DAX measure information
        """
        logger.info(f"Translating {len(calculations)} Tableau calculations to DAX")
        
        dax_measures = []
        
        for calc in calculations:
            try:
                dax_formula = self.translate_formula(calc['formula'])
                dax_measures.append({
                    'name': calc['name'],
                    'expression': dax_formula,
                    'dataType': self._map_data_type(calc['datatype'])
                })
            except Exception as e:
                logger.warning(f"Error translating calculation '{calc['name']}': {str(e)}")
                # Create a commented-out measure with the original formula for manual review
                dax_measures.append({
                    'name': calc['name'] + '_REVIEW',
                    'expression': f"/* Translation failed. Original formula: {calc['formula']} */\n/* Error: {str(e)} */\n0",
                    'dataType': 'Double'
                })
        
        return dax_measures
    
    def translate_formula(self, tableau_formula):
        """
        Translate a single Tableau formula to DAX
        
        Args:
            tableau_formula: Tableau calculation formula
            
        Returns:
            Equivalent DAX expression
        """
        # Start with the original formula
        dax_formula = tableau_formula
        
        # Substitute function names
        for tableau_func, dax_func in self.function_mapping.items():
            # Use regex to match function names followed by opening parenthesis
            pattern = r'\b' + tableau_func + r'\s*\('
            dax_formula = re.sub(pattern, dax_func + '(', dax_formula)
        
        # Handle special cases
        dax_formula = self._handle_special_cases(dax_formula)
        
        # Translate field references
        dax_formula = self._translate_field_references(dax_formula)
        
        # Translate table calculations (window functions)
        dax_formula = self._translate_table_calculations(dax_formula)
        
        return dax_formula
    
    def _handle_special_cases(self, formula):
        """Handle special cases in the translation"""
        # Replace Tableau's DATEPART with appropriate DAX functions
        formula = self._handle_datepart_functions(formula)
        
        # Replace Tableau's ATTR with appropriate DAX functions
        formula = formula.replace('ATTR(', 'VALUES(')
        
        # Replace Tableau's IIF with DAX's IF
        formula = formula.replace('IIF(', 'IF(')
        
        # Handle NULL literals
        formula = formula.replace('NULL', 'BLANK()')
        
        return formula
    
    def _handle_datepart_functions(self, formula):
        """Handle Tableau's DATEPART function which needs special treatment"""
        # Look for DATEPART patterns
        datepart_pattern = r'DATEPART\s*\(\s*[\'"]?(year|quarter|month|day|hour|minute|second)[\'"]?\s*,\s*([^)]+)\)'
        
        def datepart_replacement(match):
            date_part = match.group(1).upper()
            date_expr = match.group(2)
            
            if date_part == 'YEAR':
                return f'YEAR({date_expr})'
            elif date_part == 'QUARTER':
                return f'QUARTER({date_expr})'
            elif date_part == 'MONTH':
                return f'MONTH({date_expr})'
            elif date_part == 'DAY':
                return f'DAY({date_expr})'
            elif date_part == 'HOUR':
                return f'HOUR({date_expr})'
            elif date_part == 'MINUTE':
                return f'MINUTE({date_expr})'
            elif date_part == 'SECOND':
                return f'SECOND({date_expr})'
            else:
                return match.group(0)  # Return unchanged if no match
        
        return re.sub(datepart_pattern, datepart_replacement, formula, flags=re.IGNORECASE)
    
    def _translate_field_references(self, formula):
        """Translate Tableau field references to DAX field references"""
        # In Tableau, fields are referenced as [Field Name]
        # In DAX, fields are referenced as 'Table'[Field Name]
        
        # This is a simplified approach - in a real implementation,
        # we would need to know the table context for each field
        
        # Look for [Field Name] patterns
        field_pattern = r'\[([^\]]+)\]'
        
        def field_replacement(match):
            field_name = match.group(1)
            # In a real implementation, we would look up the table name
            # For now, we'll use a placeholder
            return f"[{field_name}]"
        
        return re.sub(field_pattern, field_replacement, formula)
    
    def _translate_table_calculations(self, formula):
        """Translate Tableau table calculations to DAX equivalents"""
        # This is a complex area requiring specialized handling
        
        # Look for common table calculation patterns
        running_sum_pattern = r'RUNNING_SUM\s*\(\s*([^)]+)\s*\)'
        running_avg_pattern = r'RUNNING_AVG\s*\(\s*([^)]+)\s*\)'
        
        # Replace RUNNING_SUM with DAX equivalent
        formula = re.sub(
            running_sum_pattern,
            lambda m: f"CALCULATE(SUM({m.group(1)}), ALLPREVIOUS())",
            formula
        )
        
        # Replace RUNNING_AVG with DAX equivalent
        formula = re.sub(
            running_avg_pattern,
            lambda m: f"CALCULATE(AVERAGE({m.group(1)}), ALLPREVIOUS())",
            formula
        )
        
        return formula
    
    def _map_data_type(self, tableau_data_type):
        """Map Tableau data types to Power BI data types"""
        type_mapping = {
            'integer': 'Int64',
            'real': 'Double',
            'string': 'String',
            'boolean': 'Boolean',
            'date': 'DateTime',
            'datetime': 'DateTime'
        }
        
        return type_mapping.get(tableau_data_type.lower(), 'String')