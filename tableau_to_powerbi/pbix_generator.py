import logging
import json
import tempfile
import os
import zipfile
import base64
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class PbixGenerator:
    """
    Generates a Power BI (.pbix) file from the converted components
    """
    
    def __init__(self):
        pass
    
    def generate(self, output_path, visual_mappings, dax_measures, data_model, dashboard_layouts):
        """
        Generate a Power BI (.pbix) file
        
        Args:
            output_path: Path where the .pbix file will be saved
            visual_mappings: List of visual configurations
            dax_measures: List of DAX measures
            data_model: Data model configuration
            dashboard_layouts: Dashboard layout information
            
        Returns:
            Path to the generated .pbix file
        """
        logger.info(f"Generating Power BI file at {output_path}")
        
        # Create a temporary directory for building the PBIX components
        temp_dir = tempfile.mkdtemp()
        try:
            # Add measures to the data model
            data_model['measures'] = dax_measures
            
            # Create the layout for each page (dashboard)
            report_pages = self._create_report_pages(dashboard_layouts, visual_mappings)
            
            # Generate the necessary files for the PBIX package
            self._generate_data_model_file(temp_dir, data_model)
            self._generate_report_file(temp_dir, report_pages)
            self._generate_connections_file(temp_dir, data_model)
            self._generate_layout_file(temp_dir, report_pages)
            self._generate_metadata_file(temp_dir)
            
            # Package everything into a PBIX file
            self._package_pbix(temp_dir, output_path)
            
            logger.info(f"Power BI file generated successfully at {output_path}")
            
            return output_path
            
        finally:
            # Clean up temporary directory
            import shutil
            shutil.rmtree(temp_dir)
    
    def _create_report_pages(self, dashboard_layouts, visual_mappings):
        """Create Power BI report pages from dashboard layouts"""
        pages = []
        
        for dashboard in dashboard_layouts:
            # Create a unique ID for the page
            page_id = str(uuid.uuid4())
            
            # Map dashboard items to visuals
            visuals = []
            for item in dashboard['items']:
                if item['type'] == 'worksheet':
                    # Find corresponding visual mapping
                    for visual in visual_mappings:
                        if visual['name'].startswith(item['name']):
                            # Create a visual with position and size
                            visual_config = {
                                'id': str(uuid.uuid4()),
                                'type': visual['type'],
                                'position': {
                                    'x': float(item.get('x', 0)),
                                    'y': float(item.get('y', 0)),
                                    'width': float(item.get('width', 200)),
                                    'height': float(item.get('height', 200))
                                },
                                'dataRoles': self._create_data_roles(visual['fields']),
                                'properties': visual['properties']
                            }
                            visuals.append(visual_config)
                            break
            
            # Create the page configuration
            page = {
                'id': page_id,
                'name': dashboard['name'],
                'displayName': dashboard['name'],
                'width': float(dashboard['size']['width']),
                'height': float(dashboard['size']['height']),
                'visuals': visuals
            }
            
            pages.append(page)
        
        return pages
    
    def _create_data_roles(self, fields):
        """Create data roles for visuals based on field mappings"""
        data_roles = []
        
        for role, field in fields.items():
            data_roles.append({
                'name': role,
                'properties': {
                    'field': field
                }
            })
        
        return data_roles
    
    def _generate_data_model_file(self, temp_dir, data_model):
        """Generate the Datamodel.json file"""
        datamodel_path = os.path.join(temp_dir, 'DataModel.json')
        
        with open(datamodel_path, 'w') as f:
            json.dump(data_model, f, indent=2)
    
    def _generate_report_file(self, temp_dir, report_pages):
        """Generate the Report.json file"""
        report = {
            'id': str(uuid.uuid4()),
            'name': 'Converted from Tableau',
            'version': '1.0',
            'pages': report_pages
        }
        
        report_path = os.path.join(temp_dir, 'Report.json')
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
    
    def _generate_connections_file(self, temp_dir, data_model):
        """Generate the Connections.json file"""
        connections = []
        
        # Extract unique connection information from data model
        for table in data_model['tables']:
            source = table.get('source', {})
            
            # Create connection entry
            connection = {
                'id': str(uuid.uuid4()),
                'name': f"Connection to {source.get('type', 'Database')}",
                'connectionType': source.get('type', 'Generic'),
                'details': {
                    'server': source.get('server', ''),
                    'database': source.get('database', ''),
                    'username': source.get('username', '')
                }
            }
            
            # Only add if not already in the list
            if not any(c['name'] == connection['name'] for c in connections):
                connections.append(connection)
        
        connections_path = os.path.join(temp_dir, 'Connections.json')
        
        with open(connections_path, 'w') as f:
            json.dump(connections, f, indent=2)
    
    def _generate_layout_file(self, temp_dir, report_pages):
        """Generate the Layout.json file"""
        layout = {
            'id': str(uuid.uuid4()),
            'pages': []
        }
        
        # Create layout entries for each page
        for page in report_pages:
            layout_page = {
                'id': page['id'],
                'name': page['name'],
                'visualContainers': []
            }
            
            # Add layout for each visual
            for visual in page.get('visuals', []):
                layout_page['visualContainers'].append({
                    'id': visual['id'],
                    'x': visual['position']['x'],
                    'y': visual['position']['y'],
                    'width': visual['position']['width'],
                    'height': visual['position']['height'],
                    'z': 0
                })
            
            layout['pages'].append(layout_page)
        
        layout_path = os.path.join(temp_dir, 'Layout.json')
        
        with open(layout_path, 'w') as f:
            json.dump(layout, f, indent=2)
    
    def _generate_metadata_file(self, temp_dir):
        """Generate the Metadata.json file with basic info"""
        metadata = {
            'version': '1.0',
            'createdBy': 'Tableau to Power BI Converter',
            'createdDateTime': datetime.now().isoformat(),
            'modifiedBy': 'Tableau to Power BI Converter',
            'modifiedDateTime': datetime.now().isoformat()
        }
        
        metadata_path = os.path.join(temp_dir, 'Metadata.json')
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _package_pbix(self, temp_dir, output_path):
        """Package all components into a .pbix file"""
        # PBIX files are essentially ZIP files with a specific structure
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as pbix:
            # Add each file in the temp directory to the PBIX
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    pbix.write(file_path, arcname)
            
            # Add a Version.txt file
            pbix.writestr('Version.txt', '1.0')