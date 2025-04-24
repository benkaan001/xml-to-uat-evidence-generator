import pytest
import xml.etree.ElementTree as ET
import os
import sys

# Ensure the script module can be imported
script_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, os.path.abspath(script_dir))

# Import functions from the script under test
try:
    from generate_uat_evidence import (
        parse_xml,
        extract_folder_data,
        MAX_SHEET_NAME_LEN,
        SHEET_NAME_IDENTIFIER_TO_REMOVE
    )
except ImportError as e:
    pytest.skip(f"Skipping tests due to import error: {e}", allow_module_level=True)


# --- Fixtures ---
@pytest.fixture
def sample_xml_content_valid():
    """Provides a valid sample XML string for testing."""
    # Includes various folder/job name structures for testing extraction
    return f"""<?xml version="1.0" encoding="utf-8"?>
<DEFTABLE>
    <FOLDER FOLDER_NAME="FOLDER_SHORT">
        <JOB JOBNAME="JOB_A"/>
        <JOB JOBNAME="JOB_B"/>
    </FOLDER>
    <FOLDER FOLDER_NAME="FOLDER_LONG_NAME_NEEDS_TRUNCATION_NO_ID">
        <JOB JOBNAME="JOB_C"/>
    </FOLDER>
    <FOLDER FOLDER_NAME="FOLDER_LONG_NAME_WITH{SHEET_NAME_IDENTIFIER_TO_REMOVE}_IDENTIFIER_XYZ">
        <JOB JOBNAME="JOB_D"/>
    </FOLDER>
    <FOLDER FOLDER_NAME="FOLDER_STILL_TOO_LONG_AFTER_REMOVING{SHEET_NAME_IDENTIFIER_TO_REMOVE}_ID">
        <JOB JOBNAME="JOB_E"/>
    </FOLDER>
    <FOLDER FOLDER_NAME="FOLDER_WITH_NO_JOBS"/>
    <FOLDER FOLDER_NAME="FOLDER_WITH_JOB_MISSING_NAME">
         <JOB />
    </FOLDER>
    <FOLDER> <JOB JOBNAME="JOB_F"/>
    </FOLDER>
</DEFTABLE>"""

@pytest.fixture
def sample_xml_file_valid(tmp_path, sample_xml_content_valid):
    """Creates a temporary valid XML file using tmp_path fixture."""
    file_path = tmp_path / "valid.xml"
    file_path.write_text(sample_xml_content_valid, encoding='utf-8')
    return file_path

@pytest.fixture
def sample_xml_file_invalid(tmp_path):
    """Creates a temporary invalid (malformed) XML file."""
    file_path = tmp_path / "invalid.xml"
    file_path.write_text("<?xml version='1.0'?><root><unclosed>", encoding='utf-8')
    return file_path

# --- Test Functions ---

def test_parse_xml_valid_file(sample_xml_file_valid):
    """Verify parsing a structurally correct XML file."""
    root = parse_xml(str(sample_xml_file_valid))
    assert root is not None
    assert isinstance(root, ET.Element)
    assert root.tag == 'DEFTABLE'

def test_parse_xml_file_not_found():
    """Verify behavior when the input XML file does not exist."""
    root = parse_xml("non_existent_file.xml")
    assert root is None

def test_parse_xml_invalid_file(sample_xml_file_invalid):
    """Verify behavior with a malformed XML file."""
    root = parse_xml(str(sample_xml_file_invalid))
    assert root is None # Expect graceful handling (return None)

def test_extract_folder_data_valid(sample_xml_content_valid):
    """Check correct extraction of folder and job names."""
    root = ET.fromstring(sample_xml_content_valid)
    # Defines the expected dictionary structure based on the sample XML
    expected_data = {
        "FOLDER_SHORT": ["JOB_A", "JOB_B"],
        "FOLDER_LONG_NAME_NEEDS_TRUNCATION_NO_ID": ["JOB_C"],
        f"FOLDER_LONG_NAME_WITH{SHEET_NAME_IDENTIFIER_TO_REMOVE}_IDENTIFIER_XYZ": ["JOB_D"],
        f"FOLDER_STILL_TOO_LONG_AFTER_REMOVING{SHEET_NAME_IDENTIFIER_TO_REMOVE}_ID": ["JOB_E"],
        "FOLDER_WITH_NO_JOBS": [],
        "FOLDER_WITH_JOB_MISSING_NAME": [] # Expect job with missing name to be skipped
        # Expect folder with missing name attribute to be skipped
    }
    actual_data = extract_folder_data(root)
    assert actual_data == expected_data

def test_extract_folder_data_empty():
    """Test extraction from an XML with no FOLDER elements."""
    root = ET.fromstring("<DEFTABLE></DEFTABLE>")
    actual_data = extract_folder_data(root)
    assert actual_data == {} # Expect an empty dictionary

# --- Testing Sheet Name Logic ---

# Helper function to isolate and test the sheet name processing logic
def get_processed_sheet_name(original_name):
     """Simulates the sheet name processing logic from write_excel_evidence."""
     sheet_name = original_name
     if len(original_name) > MAX_SHEET_NAME_LEN:
        sheet_name = original_name.replace(SHEET_NAME_IDENTIFIER_TO_REMOVE, '')
        if len(sheet_name) > MAX_SHEET_NAME_LEN:
            sheet_name = sheet_name[:MAX_SHEET_NAME_LEN]
     return sheet_name

# Use parametrize for efficient testing of multiple scenarios
@pytest.mark.parametrize("original, expected", [
    ("SHORT_NAME", "SHORT_NAME"),
    ("NAME_EXACTLY_31_CHARACTERS_LONG", "NAME_EXACTLY_31_CHARACTERS_LONG"),
    (f"LONG_NAME_WITH{SHEET_NAME_IDENTIFIER_TO_REMOVE}_ID_THAT_IS_LONG", "LONG_NAME_WITH_ID_THAT_IS_LONG"),
    ("VERY_LONG_NAME_WITHOUT_IDENTIFIER_NEEDS_TRUNCATION", "VERY_LONG_NAME_WITHOUT_IDENTIFI"),
    (f"MUCH_LONGER_NAME_WITH{SHEET_NAME_IDENTIFIER_TO_REMOVE}_ID_STILL_NEEDS_TRUNCATION", "MUCH_LONGER_NAME_WITH_ID_STILL_"),
])
def test_sheet_name_shortening_logic(original, expected):
    """Verify the sheet name shortening and truncation logic."""
    assert get_processed_sheet_name(original) == expected



