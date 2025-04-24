import xml.etree.ElementTree as ET
import pandas as pd
import argparse
import sys
import os
from typing import Dict, List, Optional

MAX_SHEET_NAME_LEN = 31
SHEET_NAME_IDENTIFIER_TO_REMOVE = "-DATAMART"

def parse_xml(xml_path: str) -> Optional[ET.Element]:
    """
    Parses the input XML file.

    Args:
        xml_path: Path to the input XML file.

    Returns:
        The root element of the parsed XML tree, or None if an error occurs.
    """
    if not os.path.exists(xml_path):
        print(f"Error: Input XML file not found at {xml_path}", file=sys.stderr)
        return None
    try:
        tree = ET.parse(xml_path)
        return tree.getroot()
    except ET.ParseError as e:
        print(f"Error: Failed to parse XML file {xml_path}. Details: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred during XML parsing: {e}", file=sys.stderr)
        return None

def extract_folder_data(root: ET.Element) -> Dict[str, List[str]]:
    """
    Extracts folder and job names from the XML root element.

    Args:
        root: The root element of the XML tree.

    Returns:
        A dictionary where keys are folder names and values are lists of job names.
    """
    folder_data: Dict[str, List[str]] = {}
    try:
        for folder in root.iter('FOLDER'):
            folder_name = folder.attrib.get('FOLDER_NAME')
            if not folder_name:
                print(f"Warning: Skipping FOLDER element with missing FOLDER_NAME attribute.", file=sys.stderr)
                continue

            folder_data[folder_name] = []
            for job in folder.iter('JOB'):
                job_name = job.attrib.get('JOBNAME')
                if job_name:
                    folder_data[folder_name].append(job_name)
                else:
                     print(f"Warning: Skipping JOB element with missing JOBNAME attribute within FOLDER '{folder_name}'.", file=sys.stderr)

    except AttributeError as e:
         print(f"Error: XML structure might be different than expected. Missing attribute? Details: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during data extraction: {e}", file=sys.stderr)

    return folder_data

def write_excel_evidence(folder_data: Dict[str, List[str]], output_path: str) -> bool:
    """
    Writes the extracted folder and job data to a multi-sheet Excel file.

    Args:
        folder_data: Dictionary containing folder and job names.
        output_path: Path for the output Excel file.

    Returns:
        True if the file was written successfully, False otherwise.
    """
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        with pd.ExcelWriter(output_path) as writer:
            for folder_name_original, job_names in folder_data.items():
                # Shorten sheet name if it exceeds limit, mimicking original logic
                sheet_name = folder_name_original
                if len(folder_name_original) > MAX_SHEET_NAME_LEN:
                    sheet_name = folder_name_original.replace(SHEET_NAME_IDENTIFIER_TO_REMOVE, '')
                    # Further truncate if still too long after replacement
                    if len(sheet_name) > MAX_SHEET_NAME_LEN:
                         sheet_name = sheet_name[:MAX_SHEET_NAME_LEN]
                    print(f"Shortened sheet name from '{folder_name_original}' to '{sheet_name}'")

                df = pd.DataFrame({'Job Name': job_names})
                # Write data starting from the second row and second column
                df.to_excel(writer,
                            sheet_name=sheet_name,
                            index=False,
                            startrow=1,
                            startcol=1)
        return True
    except PermissionError:
         print(f"Error: Permission denied. Cannot write to {output_path}. Check file permissions or if the file is open.", file=sys.stderr)
         return False
    except Exception as e:
        print(f"Error: Failed to write Excel file {output_path}. Details: {e}", file=sys.stderr)
        return False

def main():
    """
    Main function to parse arguments and orchestrate the UAT evidence generation.
    """
    parser = argparse.ArgumentParser(description="Generate a multi-sheet Excel UAT evidence document from a Control-M XML definition file.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input Control-M XML file.")
    parser.add_argument("-o", "--output", required=True, help="Path for the output Excel evidence file.")

    args = parser.parse_args()

    print(f"Starting UAT evidence generation...")
    print(f"Input XML: {args.input}")
    print(f"Output Excel: {args.output}")

    # 1. Parse XML
    xml_root = parse_xml(args.input)
    if xml_root is None:
        sys.exit(1) # Exit if parsing failed

    # 2. Extract Data
    folder_job_data = extract_folder_data(xml_root)
    if not folder_job_data:
         print("Warning: No folder data extracted. The input XML might be empty or lack FOLDER/JOB elements.", file=sys.stderr)

    # 3. Write Excel
    success = write_excel_evidence(folder_job_data, args.output)
    if success:
        print(f"Successfully created UAT evidence file: {args.output}")
    else:
        print("Failed to create UAT evidence file.", file=sys.stderr)
        sys.exit(1) # Exit if writing failed

if __name__ == "__main__":
    main()
