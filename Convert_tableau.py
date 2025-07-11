from tableau_to_powerbi.converter import TableauToPowerBIConverter
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_tableau.py <path_to_tableau_file.twbx>")
        return
    
    tableau_file = sys.argv[1]
    if not os.path.exists(tableau_file):
        print(f"Error: File not found: {tableau_file}")
        return
    
    print(f"Converting {tableau_file}...")
    converter = TableauToPowerBIConverter()
    
    try:
        output_dir = converter.convert(tableau_file)
        print(f"\nConversion completed successfully!")
        print(f"Output directory: {output_dir}")
        print("\nInstructions:")
        print("1. Open Power BI Desktop")
        print("2. Use the extracted data files and configuration files to recreate your dashboard")
        print("3. Refer to the README.md file in the output directory for detailed instructions")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")

if __name__ == "__main__":
    main()
