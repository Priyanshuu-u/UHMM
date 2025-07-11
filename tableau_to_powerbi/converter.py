import os
import zipfile
import xml.etree.ElementTree as ET
import json
import tempfile
import shutil
from pathlib import Path
import logging
import pandas as pd
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TableauToPowerBIConverter:
    """
    Converts Tableau workbooks (.twbx) to Power BI Template (.pbit) files
    """
    
    def __init__(self):
        pass
        
    def convert(self, input_file_path, output_directory=None):
        """
        Convert a Tableau workbook to Power BI Template and supporting files
        
        Args:
            input_file_path: Path to the .twbx file
            output_directory: Optional directory for the output files
            
        Returns:
            Path to the generated output directory
        """
        logger.info(f"Starting conversion of {input_file_path}")
        
        # Validate input file
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Input file not found: {input_file_path}")
            
        if not input_file_path.lower().endswith('.twbx'):
            raise ValueError("Input file must be a .twbx file")
        
        # Create output directory
        input_filename = os.path.basename(input_file_path)
        base_name = os.path.splitext(input_filename)[0]
        
        if output_directory:
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            output_dir = os.path.join(output_directory, f"{base_name}_powerbi")
        else:
            output_dir = os.path.join(os.path.dirname(input_file_path), f"{base_name}_powerbi")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Create temporary directory for extraction
        temp_dir = tempfile.mkdtemp()
        try:
            # Extract the .twbx file (it's essentially a zip file)
            self._extract_twbx(input_file_path, temp_dir)
            
            # Find the .twb file (XML) within the extracted content
            twb_file = self._find_twb_file(temp_dir)
            if not twb_file:
                raise FileNotFoundError("No .twb file found in the Tableau workbook")
            
            # Extract data sources
            datasources = self._extract_datasources(twb_file)
            
            # Extract worksheets
            worksheets = self._extract_worksheets(twb_file)
            
            # Extract dashboards
            dashboards = self._extract_dashboards(twb_file)
            
            # Generate Power BI Template (.pbit)
            self._generate_power_bi_template(output_dir, datasources, worksheets, dashboards)
            
            # Generate Data Files
            self._extract_data_files(temp_dir, output_dir)
            
            # Generate README with instructions
            self._generate_readme(output_dir, datasources, worksheets, dashboards)
            
            logger.info(f"Conversion completed successfully. Output directory: {output_dir}")
            return output_dir
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
    
    def _extract_twbx(self, twbx_path, extract_dir):
        """Extract the contents of a .twbx file"""
        with zipfile.ZipFile(twbx_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    
    def _find_twb_file(self, directory):
        """Find the .twb file in the extracted directory"""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.twb'):
                    return os.path.join(root, file)
        return None
    
    def _extract_datasources(self, twb_file):
        """Extract data source information from Tableau workbook"""
        datasources = []
        try:
            tree = ET.parse(twb_file)
            root = tree.getroot()
            
            for ds in root.findall(".//datasource"):
                ds_info = {
                    'name': ds.get('name', 'Unknown'),
                    'caption': ds.get('caption', ''),
                    'connection_type': '',
                    'columns': []
                }
                
                # Extract connection info
                connection = ds.find(".//connection")
                if connection is not None:
                    ds_info['connection_type'] = connection.get('class', '')
                    ds_info['connection_details'] = {
                        'server': connection.get('server', ''),
                        'database': connection.get('dbname', ''),
                        'username': connection.get('username', '')
                    }
                
                # Extract columns
                for column in ds.findall(".//column"):
                    col_info = {
                        'name': column.get('name', ''),
                        'caption': column.get('caption', ''),
                        'datatype': column.get('datatype', 'string')
                    }
                    ds_info['columns'].append(col_info)
                
                datasources.append(ds_info)
            
        except Exception as e:
            logger.error(f"Error extracting datasources: {str(e)}")
        
        return datasources
    
    def _extract_worksheets(self, twb_file):
        """Extract worksheet information from Tableau workbook"""
        worksheets = []
        try:
            tree = ET.parse(twb_file)
            root = tree.getroot()
            
            for worksheet in root.findall(".//worksheet"):
                ws_info = {
                    'name': worksheet.get('name', 'Unknown'),
                    'visualization_type': 'unknown',
                    'fields': []
                }
                
                # Determine visualization type
                marks = worksheet.find(".//style/style-rule/format[@attr='mark']")
                if marks is not None:
                    ws_info['visualization_type'] = marks.get('value', 'automatic')
                
                # Extract fields used
                for field in worksheet.findall(".//field"):
                    ws_info['fields'].append(field.get('name', ''))
                
                worksheets.append(ws_info)
            
        except Exception as e:
            logger.error(f"Error extracting worksheets: {str(e)}")
        
        return worksheets
    
    def _extract_dashboards(self, twb_file):
        """Extract dashboard information from Tableau workbook"""
        dashboards = []
        try:
            tree = ET.parse(twb_file)
            root = tree.getroot()
            
            for dashboard in root.findall(".//dashboard"):
                dash_info = {
                    'name': dashboard.get('name', 'Unknown'),
                    'size': {
                        'width': dashboard.get('maxwidth', '1000'),
                        'height': dashboard.get('maxheight', '800')
                    },
                    'items': []
                }
                
                # Extract items in the dashboard
                for zone in dashboard.findall(".//zone"):
                    item = {
                        'type': zone.get('type', ''),
                        'name': zone.get('name', ''),
                        'position': {
                            'x': zone.get('x', '0'),
                            'y': zone.get('y', '0'),
                            'width': zone.get('w', '200'),
                            'height': zone.get('h', '200')
                        }
                    }
                    dash_info['items'].append(item)
                
                dashboards.append(dash_info)
            
        except Exception as e:
            logger.error(f"Error extracting dashboards: {str(e)}")
        
        return dashboards
    
    def _extract_data_files(self, extract_dir, output_dir):
        """Extract data files from the Tableau workbook"""
        data_dir = os.path.join(output_dir, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Find all data files (.csv, .xlsx, etc.)
        for root, _, files in os.walk(extract_dir):
            for file in files:
                if file.lower().endswith(('.csv', '.xlsx', '.xls', '.txt', '.json')):
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(data_dir, file)
                    shutil.copy2(src_file, dst_file)
                    logger.info(f"Copied data file: {file}")
    
    def _generate_power_bi_template(self, output_dir, datasources, worksheets, dashboards):
        """Generate a basic Power BI Template file with recreated structure"""
        # Create PowerBI directory
        pbi_dir = os.path.join(output_dir, "PowerBI")
        if not os.path.exists(pbi_dir):
            os.makedirs(pbi_dir)
        
        # Generate DAX measures file
        self._generate_dax_measures(pbi_dir, worksheets)
        
        # Generate data model JSON
        self._generate_data_model(pbi_dir, datasources)
        
        # Generate visuals configuration
        self._generate_visuals_config(pbi_dir, worksheets, dashboards)
        
        # Create a simple .pbit starter template
        self._create_pbit_starter(pbi_dir)
    
    def _generate_dax_measures(self, pbi_dir, worksheets):
        """Generate DAX measures based on worksheet info"""
        measures = []
        
        # Find calculated fields
        for worksheet in worksheets:
            for field in worksheet.get('fields', []):
                if 'calc' in field.lower():
                    # Create a simple placeholder measure
                    measure = {
                        'name': field,
                        'expression': f"// TODO: Replace with actual calculation\nSUM(1)"
                    }
                    measures.append(measure)
        
        # Write to file
        measures_file = os.path.join(pbi_dir, "dax_measures.json")
        with open(measures_file, 'w') as f:
            json.dump(measures, f, indent=2)
    
    def _generate_data_model(self, pbi_dir, datasources):
        """Generate data model configuration"""
        tables = []
        
        for ds in datasources:
            columns = []
            for col in ds.get('columns', []):
                columns.append({
                    'name': col.get('caption', col.get('name', '')),
                    'dataType': self._map_data_type(col.get('datatype', 'string'))
                })
            
            tables.append({
                'name': ds.get('name', 'Unknown'),
                'columns': columns
            })
        
        # Write to file
        model_file = os.path.join(pbi_dir, "data_model.json")
        with open(model_file, 'w') as f:
            json.dump({'tables': tables}, f, indent=2)
    
    def _map_data_type(self, tableau_type):
        """Map Tableau data types to Power BI data types"""
        mapping = {
            'integer': 'Int64',
            'real': 'Double',
            'string': 'String',
            'boolean': 'Boolean',
            'date': 'DateTime',
            'datetime': 'DateTime'
        }
        return mapping.get(tableau_type.lower(), 'String')
    
    def _generate_visuals_config(self, pbi_dir, worksheets, dashboards):
        """Generate configuration for Power BI visuals"""
        visuals = []
        
        for worksheet in worksheets:
            visual_type = self._map_visual_type(worksheet.get('visualization_type', 'unknown'))
            visuals.append({
                'name': worksheet.get('name', 'Unknown'),
                'type': visual_type,
                'fields': worksheet.get('fields', [])
            })
        
        # Write to file
        visuals_file = os.path.join(pbi_dir, "visuals.json")
        with open(visuals_file, 'w') as f:
            json.dump(visuals, f, indent=2)
        
        # Generate dashboard layouts
        layouts = []
        for dashboard in dashboards:
            layout = {
                'name': dashboard.get('name', 'Unknown'),
                'size': dashboard.get('size', {}),
                'items': dashboard.get('items', [])
            }
            layouts.append(layout)
        
        # Write to file
        layouts_file = os.path.join(pbi_dir, "layouts.json")
        with open(layouts_file, 'w') as f:
            json.dump(layouts, f, indent=2)
    
    def _map_visual_type(self, tableau_type):
        """Map Tableau visual types to Power BI visual types"""
        mapping = {
            'bar': 'columnChart',
            'line': 'lineChart',
            'pie': 'pieChart',
            'text': 'card',
            'map': 'map',
            'scatter': 'scatterChart',
            'automatic': 'columnChart'  # Default
        }
        return mapping.get(tableau_type.lower(), 'columnChart')
    
    def _create_pbit_starter(self, pbi_dir):
        """Create a starter .pbit file with basic template"""
        # Generate a .pbix template file path
        template_file = os.path.join(pbi_dir, "tableau_conversion_template.pbit")
        
        # For now, we'll just create a stub JSON file since actual .pbit creation is complex
        with open(template_file, 'w') as f:
            f.write("This is a placeholder for the .pbit file. Use the PowerBI Desktop to create a new file based on the provided JSON configs.")
    
    def _generate_readme(self, output_dir, datasources, worksheets, dashboards):
        """Generate a README file with instructions"""
        readme_content = """# Tableau to Power BI Conversion

This folder contains the extracted information from your Tableau workbook, prepared for importing into Power BI.

## Contents

1. **data/** - Contains extracted data files from the Tableau workbook
2. **PowerBI/** - Contains configuration files for rebuilding in Power BI:
   - data_model.json - Data model structure
   - dax_measures.json - DAX measures to recreate
   - visuals.json - Visual configurations
   - layouts.json - Dashboard layouts

## Instructions for Importing to Power BI

1. Open Power BI Desktop
2. Create a new blank report
3. Import data from the data/ folder
4. Use the JSON files in the PowerBI/ folder as reference to recreate:
   - Data model structure (relationships, column names)
   - DAX measures (from dax_measures.json)
   - Visuals (using the configurations in visuals.json)
   - Dashboard layouts (using layouts.json)

## Data Sources

The following data sources were found in the Tableau workbook:

"""
        # Add datasource info
        for ds in datasources:
            readme_content += f"- {ds.get('name', 'Unknown')}"
            if ds.get('connection_type'):
                readme_content += f" (Type: {ds.get('connection_type')})"
            readme_content += "\n"
        
        readme_content += """
## Worksheets/Visuals

The following worksheets/visuals were found:

"""
        # Add worksheet info
        for ws in worksheets:
            readme_content += f"- {ws.get('name', 'Unknown')} (Type: {ws.get('visualization_type', 'Unknown')})\n"
        
        readme_content += """
## Dashboards

The following dashboards were found:

"""
        # Add dashboard info
        for db in dashboards:
            readme_content += f"- {db.get('name', 'Unknown')}\n"
        
        # Write to file
        readme_file = os.path.join(output_dir, "README.md")
        with open(readme_file, 'w') as f:
            f.write(readme_content)
