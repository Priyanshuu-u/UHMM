import logging
import json

logger = logging.getLogger(__name__)

class DataModelBuilder:
    """
    Builds a Power BI data model from Tableau data sources and relationships
    """
    
    def __init__(self):
        pass
    
    def build_model(self, data_sources, relationships):
        """
        Build a Power BI data model from Tableau metadata
        
        Args:
            data_sources: List of Tableau data sources
            relationships: List of relationships between data sources
            
        Returns:
            Dictionary representing the Power BI data model
        """
        logger.info(f"Building data model from {len(data_sources)} data sources")
        
        tables = self._create_tables(data_sources)
        relationships = self._create_relationships(relationships, tables)
        
        data_model = {
            'tables': tables,
            'relationships': relationships,
            'measures': []  # Measures will be added separately
        }
        
        return data_model
    
    def _create_tables(self, data_sources):
        """Create Power BI tables from Tableau data sources"""
        tables = []
        
        for ds in data_sources:
            # Create a table for each data source
            table = {
                'name': ds['name'],
                'columns': self._create_columns(ds['columns']),
                'isHidden': False,
                'source': self._create_source_info(ds['connection'])
            }
            
            tables.append(table)
        
        return tables
    
    def _create_columns(self, tableau_columns):
        """Create Power BI columns from Tableau columns"""
        columns = []
        
        for col in tableau_columns:
            column = {
                'name': col.get('caption', col['name']),
                'dataType': self._map_data_type(col['datatype']),
                'sourceColumn': col['name'],
                'formatString': self._get_format_string(col['datatype']),
                'isHidden': False
            }
            
            columns.append(column)
        
        return columns
    
    def _create_source_info(self, connection):
        """Create source information for Power BI"""
        connection_type = connection.get('class', '').lower()
        
        # Handle different connection types
        if 'oracle' in connection_type:
            return {
                'type': 'Oracle',
                'server': connection.get('server', ''),
                'database': connection.get('dbname', ''),
                'username': connection.get('username', '')
            }
        elif 'mysql' in connection_type:
            return {
                'type': 'MySQL',
                'server': connection.get('server', ''),
                'database': connection.get('dbname', ''),
                'username': connection.get('username', '')
            }
        elif 'sqlserver' in connection_type:
            return {
                'type': 'SQL',
                'server': connection.get('server', ''),
                'database': connection.get('dbname', ''),
                'username': connection.get('username', '')
            }
        elif 'postgresql' in connection_type:
            return {
                'type': 'PostgreSQL',
                'server': connection.get('server', ''),
                'database': connection.get('dbname', ''),
                'username': connection.get('username', '')
            }
        elif 'excel' in connection_type or 'csv' in connection_type:
            return {
                'type': 'File',
                'path': connection.get('dbname', '')
            }
        else:
            # Generic source for other types
            return {
                'type': 'Generic',
                'connection': json.dumps(connection)
            }
    
    def _create_relationships(self, tableau_relationships, tables):
        """Create Power BI relationships from Tableau relationships"""
        relationships = []
        
        for rel in tableau_relationships:
            for clause in rel.get('join', []):
                # Extract table and column names from lhs and rhs
                lhs_parts = clause['lhs'].split('.')
                rhs_parts = clause['rhs'].split('.')
                
                if len(lhs_parts) >= 2 and len(rhs_parts) >= 2:
                    relationship = {
                        'fromTable': lhs_parts[0],
                        'fromColumn': lhs_parts[1],
                        'toTable': rhs_parts[0],
                        'toColumn': rhs_parts[1],
                        'cardinality': 'ManyToOne',  # Default, could be more intelligent
                        'crossFilteringBehavior': 'BothDirections'
                    }
                    
                    relationships.append(relationship)
        
        return relationships
    
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
    
    def _get_format_string(self, data_type):
        """Get appropriate format string based on data type"""
        format_mapping = {
            'integer': '#,0',
            'real': '#,0.00',
            'date': 'MM/dd/yyyy',
            'datetime': 'MM/dd/yyyy hh:mm:ss',
            'currency': '$#,0.00'
        }
        
        return format_mapping.get(data_type.lower(), '')