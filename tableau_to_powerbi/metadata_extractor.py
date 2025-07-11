import xml.etree.ElementTree as ET
import logging
import re

logger = logging.getLogger(__name__)

class TableauMetadataExtractor:
    """
    Extracts metadata from a Tableau workbook (.twb) file
    """
    
    def __init__(self):
        self.namespaces = {
            'tableau': 'http://www.tableausoftware.com/xml/tableau'
        }
    
    def extract_metadata(self, twb_file_path):
        """
        Extract all relevant metadata from a Tableau workbook
        
        Args:
            twb_file_path: Path to the .twb XML file
            
        Returns:
            Dictionary containing worksheets, calculations, data sources, 
            relationships, and dashboards information
        """
        logger.info(f"Extracting metadata from {twb_file_path}")
        
        try:
            tree = ET.parse(twb_file_path)
            root = tree.getroot()
            
            metadata = {
                'worksheets': self._extract_worksheets(root),
                'calculations': self._extract_calculations(root),
                'data_sources': self._extract_data_sources(root),
                'relationships': self._extract_relationships(root),
                'dashboards': self._extract_dashboards(root)
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            raise
    
    def _extract_worksheets(self, root):
        """Extract worksheet information"""
        worksheets = []
        
        for worksheet in root.findall('.//tableau:worksheet', self.namespaces):
            worksheet_name = worksheet.get('name', '')
            
            # Extract visualizations within the worksheet
            visualizations = []
            for vis in worksheet.findall('.//tableau:pane', self.namespaces):
                vis_type = self._determine_visualization_type(vis)
                visualizations.append({
                    'type': vis_type,
                    'marks': self._extract_marks(vis),
                    'encodings': self._extract_encodings(vis)
                })
            
            # Extract filters
            filters = []
            for filter_elem in worksheet.findall('.//tableau:filter', self.namespaces):
                filters.append({
                    'field': filter_elem.get('field', ''),
                    'type': filter_elem.get('type', ''),
                    'values': self._extract_filter_values(filter_elem)
                })
            
            worksheets.append({
                'name': worksheet_name,
                'visualizations': visualizations,
                'filters': filters,
                'fields': self._extract_worksheet_fields(worksheet)
            })
        
        return worksheets
    
    def _extract_calculations(self, root):
        """Extract calculation formulas"""
        calculations = []
        
        for calc in root.findall('.//tableau:calculation', self.namespaces):
            formula = calc.get('formula', '')
            name = calc.get('name', '')
            
            if formula and name:
                calculations.append({
                    'name': name,
                    'formula': formula,
                    'datatype': calc.get('datatype', 'string')
                })
        
        return calculations
    
    def _extract_data_sources(self, root):
        """Extract data source information"""
        data_sources = []
        
        for ds in root.findall('.//tableau:datasource', self.namespaces):
            connection_info = {}
            connection = ds.find('.//tableau:connection', self.namespaces)
            if connection is not None:
                connection_info = {
                    'class': connection.get('class', ''),
                    'server': connection.get('server', ''),
                    'dbname': connection.get('dbname', ''),
                    'username': connection.get('username', '')
                }
            
            # Extract columns/fields
            columns = []
            for column in ds.findall('.//tableau:column', self.namespaces):
                columns.append({
                    'name': column.get('name', ''),
                    'datatype': column.get('datatype', 'string'),
                    'caption': column.get('caption', '')
                })
            
            data_sources.append({
                'name': ds.get('name', ''),
                'connection': connection_info,
                'columns': columns
            })
        
        return data_sources
    
    def _extract_relationships(self, root):
        """Extract relationships between data sources"""
        relationships = []
        
        for relation in root.findall('.//tableau:relation', self.namespaces):
            relationships.append({
                'type': relation.get('type', 'inner'),
                'join': self._extract_join_conditions(relation)
            })
        
        return relationships
    
    def _extract_dashboards(self, root):
        """Extract dashboard information"""
        dashboards = []
        
        for dashboard in root.findall('.//tableau:dashboard', self.namespaces):
            dashboard_items = []
            
            for item in dashboard.findall('.//tableau:zone', self.namespaces):
                dashboard_items.append({
                    'type': item.get('type', ''),
                    'name': item.get('name', ''),
                    'width': item.get('width', ''),
                    'height': item.get('height', ''),
                    'x': item.get('x', ''),
                    'y': item.get('y', '')
                })
            
            dashboards.append({
                'name': dashboard.get('name', ''),
                'size': {
                    'width': dashboard.get('maxwidth', '1000'),
                    'height': dashboard.get('maxheight', '800')
                },
                'items': dashboard_items
            })
        
        return dashboards
    
    # Helper methods
    def _determine_visualization_type(self, vis_element):
        """Determine the type of visualization from the XML element"""
        # Logic to determine if it's a bar chart, line chart, etc.
        # This is a simplified version - real implementation would be more complex
        mark_type = vis_element.find('.//tableau:mark', self.namespaces)
        if mark_type is not None:
            return mark_type.get('type', 'automatic')
        return 'automatic'
    
    def _extract_marks(self, vis_element):
        """Extract mark properties from visualization"""
        marks = {}
        mark_elem = vis_element.find('.//tableau:mark', self.namespaces)
        if mark_elem is not None:
            for encoding in mark_elem.findall('.//tableau:encoding', self.namespaces):
                field = encoding.get('field', '')
                marks[encoding.get('type', '')] = field
        return marks
    
    def _extract_encodings(self, vis_element):
        """Extract visual encodings (color, size, etc.)"""
        encodings = {}
        for encoding in vis_element.findall('.//tableau:encoding', self.namespaces):
            field = encoding.get('field', '')
            encodings[encoding.get('type', '')] = field
        return encodings
    
    def _extract_filter_values(self, filter_element):
        """Extract values from a filter"""
        values = []
        for value in filter_element.findall('.//tableau:value', self.namespaces):
            values.append(value.text)
        return values
    
    def _extract_worksheet_fields(self, worksheet):
        """Extract fields used in a worksheet"""
        fields = []
        for field in worksheet.findall('.//tableau:field', self.namespaces):
            fields.append(field.get('name', ''))
        return fields
    
    def _extract_join_conditions(self, relation):
        """Extract join conditions from a relation"""
        conditions = []
        for clause in relation.findall('.//tableau:clause', self.namespaces):
            conditions.append({
                'lhs': clause.get('lhs', ''),
                'rhs': clause.get('rhs', ''),
                'operator': clause.get('op', '=')
            })
        return conditions