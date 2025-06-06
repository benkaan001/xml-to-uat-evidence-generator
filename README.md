# XML to UAT Evidence Generator

[![CI Pipeline](https://github.com/benkaan001/xml-to-uat-evidence-generator/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/benkaan001/xml-to-uat-evidence-generator/actions/workflows/ci.yml)

This script streamlines the User Acceptance Testing (UAT) evidence collection process for deployments managed via Control-M (or similar XML-based configuration).

## Problem Solved

In many deployment processes, especially those involving regulated environments or complex integrations, developers need to provide evidence that their changes work correctly before deploying to pre-production or production environments. This often involves capturing screenshots or logs for each component (e.g., job) within a deployment unit (e.g., a Control-M folder).

Manually creating documentation templates (like Word documents or spreadsheets) for each deployment can be time-consuming and prone to errors. The previous process involved navigating complex folder structures and potentially confusing links within documents, making it difficult for both developers adding evidence and clients reviewing it.

This script automates the creation of a structured UAT evidence template in Excel format directly from the source configuration XML (e.g., Control-M folder export).

## Functionality

1. **Parses XML:** Reads an XML file containing job scheduling definitions (specifically `<FOLDER>` and `<JOB>` elements with `FOLDER_NAME` and `JOBNAME` attributes).
2. **Extracts Structure:** Identifies all jobs listed within each folder.
3. **Generates Excel Template:** Creates a multi-sheet Excel workbook where:
   * Each sheet corresponds to one `<FOLDER>` element from the XML.
   * The sheet name is derived from the `FOLDER_NAME`. If the `FOLDER_NAME` exceeds 31 characters and contains a specific identifier (`-DATAMART` in this sample), the identifier is removed to shorten the name. If it's still too long, it's truncated.
   * Each sheet lists the `JOBNAME`s belonging to that folder in a column, providing a clear structure for adding test evidence.
   * The job names are written starting from cell B2 (column 1, row 1 using 0-based indexing in pandas `to_excel`) to leave space for headers or instructions.

## Setup

1. **Clone the repository:**
   ```
   git clone <your-repository-url>
   cd xml-to-uat-evidence-generator

   ```
2. **Create a virtual environment (recommended):**
   ```
   # On macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate

   # On Windows
   python -m venv .venv
   .\.venv\Scripts\activate

   ```
3. **Install dependencies:**
   ```
   pip install -r requirements.txt

   ```

## Usage

Run the script from the command line, providing the path to the input XML and the desired path for the output Excel file.

```
python src/generate_uat_evidence.py --input <path_to_input_xml> --output <path_to_output_excel>

```

**Example using sample data:**

```
python src/generate_uat_evidence.py --input sample_data/sample_config.xml --output sample_output/sample_uat_evidence_results.xlsx

```

**Expected Output:**

The script will print status messages and create the Excel file at the specified output path. You might see messages indicating sheet name shortening if applicable:

```
Starting UAT evidence generation...
Input XML: sample_data/sample_config.xml
Output Excel: sample_output/sample_uat_evidence_results.xlsx
Shortened sheet name from 'OPS-PREPROD-SAFETY-INCIDENT-DATAMART-TRACKING-201' to 'OPS-PREPROD-SAFETY-INCIDENT-TRA'
Shortened sheet name from 'REV-PROD-WAYBILL-PROC-DATAMART-1060' to 'REV-PROD-WAYBILL-PROC-1060'
Shortened sheet name from 'SCM-PROD-INVENTORY-MGMT-DATAMART-INV01' to 'SCM-PROD-INVENTORY-MGMT-INV01'
Successfully created UAT evidence file: sample_output/sample_uat_evidence_results.xlsx

```

## Testing

Unit tests are included to verify the core logic of the script. They cover XML parsing, data extraction, and the sheet name shortening/truncation rules.

To run the tests locally:

1. Ensure you have installed the dependencies (`pip install -r requirements.txt`).
2. Navigate to the root directory of the repository.
3. Run `pytest`:
   ```
   pytest

   ```

   All tests should pass.

A Continuous Integration (CI) workflow is set up using GitHub Actions (`.github/workflows/ci.yml`). This workflow automatically runs the linter (`flake8`) and the unit tests (`pytest`) on pushes and pull requests to the main branch, ensuring code quality and correctness.

## Sample Data

* `sample_data/sample_config.xml`: An anonymized XML file mimicking the structure and complexity of a Control-M export, including long folder names with the `-DATAMART` identifier for testing purposes.
* `sample_output/sample_uat_evidence_results.xlsx`: An example Excel file generated by running the script with the sample input.

## Confidentiality Note

This repository uses anonymized/fictitious data. The structure and logic are representative of a real-world automation task.
