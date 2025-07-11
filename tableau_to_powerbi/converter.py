import os
import zipfile
import xml.etree.ElementTree as ET
import json
import tempfile
import shutil
from pathlib import Path
import logging
from .visual_mapper import VisualMapper
from .dax_translator import DaxTranslator
from .data_model_builder import DataModelBuilder
from .pbix_generator import PbixGenerator
from .metadata_extractor import TableauMetadataExtractor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TableauToPowerBIConverter:
    """
    Main class for converting Tableau workbooks (.twbx) to Power BI (.pbix) files
    """
    
    def __init__(self):
        self.visual_mapper = VisualMapper()
        self.dax_translator = DaxTranslator()
        self.data_model_builder = DataModelBuilder()
        self.pbix_generator = PbixGenerator()
        self.metadata_extractor = TableauMetadataExtractor()
        
    def convert(self, input_file_path, output_directory=None):
        """
        Convert a Tableau workbook to a Power BI file
        
        Args:
            input_file_path: Path to the .twbx file
            output_directory: Optional directory for the output file
            
        Returns:
            Path to the generated .pbix file
        """
        logger.info(f"Starting conversion of {input_file_path}")
        
        # Validate input file
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Input file not found: {input_file_path}")
            
        if not input_file_path.lower().endswith('.twbx'):
            raise ValueError("Input file must be a .twbx file")
        
        # Create temporary directory for extraction
        temp_dir = tempfile.mkdtemp()
        try:
            # Extract the .twbx file (it's essentially a zip file)
            self._extract_twbx(input_file_path, temp_dir)
            
            # Find the .twb file (XML) within the extracted content
            twb_file = self._find_twb_file(temp_dir)
            if not twb_file:
                raise FileNotFoundError("No .twb file found in the Tableau workbook")
            
            # Extract metadata from the Tableau workbook
            tableau_metadata = self.metadata_extractor.extract_metadata(twb_file)
            
            # Map visualizations from Tableau to Power BI
            visual_mappings = self.visual_mapper.map_visuals(tableau_metadata['worksheets'])
            
            # Translate Tableau calculations to DAX
            dax_measures = self.dax_translator.translate_calculations(tableau_metadata['calculations'])
            
            # Build the data model for Power BI
            data_model = self.data_model_builder.build_model(
                tableau_metadata['data_sources'],
                tableau_metadata['relationships']
            )
            
            # Determine output file path
            input_filename = os.path.basename(input_file_path)
            output_filename = f"{os.path.splitext(input_filename)[0]}.pbix"
            
            if output_directory:
                if not os.path.exists(output_directory):
                    os.makedirs(output_directory)
                output_path = os.path.join(output_directory, output_filename)
            else:
                output_path = os.path.join(os.path.dirname(input_file_path), output_filename)
            
            # Generate the Power BI file
            self.pbix_generator.generate(
                output_path,
                visual_mappings,
                dax_measures,
                data_model,
                tableau_metadata['dashboards']
            )
            
            logger.info(f"Conversion completed successfully. Output file: {output_path}")
            return output_path
            
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