import argparse
import logging
import os
import sys
from .converter import TableauToPowerBIConverter

def main():
    """
    Command-line interface for the Tableau to Power BI converter
    """
    parser = argparse.ArgumentParser(
        description='Convert Tableau workbooks (.twbx) to Power BI (.pbix) files'
    )
    
    parser.add_argument(
        'input_file',
        help='Path to the Tableau workbook (.twbx) file'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Directory where the output Power BI file will be saved'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    if not args.input_file.lower().endswith('.twbx'):
        print("Error: Input file must be a Tableau workbook (.twbx) file")
        sys.exit(1)
    
    # Create the converter
    converter = TableauToPowerBIConverter()
    
    try:
        # Convert the file
        output_file = converter.convert(args.input_file, args.output)
        print(f"Conversion successful! Output file: {output_file}")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()