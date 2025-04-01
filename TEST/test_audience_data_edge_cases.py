"""
Test file for the extract_audience_data function focusing on edge cases.
"""

import os
import sys
import json
import base64
import asyncio
import shutil
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock
import uuid
import re

# Add the project root directory to the Python path
sys.path.append("/Users/meirsabag/Public/browser_use_ver4_newVersion")

# Import the custom controller
from remote_tools_folders.custom_controller import extract_audience_data, ExtractAudienceDataAction
from browser_use.agent.views import ActionResult

class MockBrowserContext:
    """A mock browser context for testing purposes"""
    def __init__(self, screenshot_data="mock_base64_data"):
        self.screenshot_data = screenshot_data
        
    async def get_current_page(self):
        return None
        
    async def take_screenshot(self, full_page=False):
        """Return the predefined screenshot data"""
        return self.screenshot_data

# Create a mock class for the anthropic.Anthropic client
class MockAnthropicClient:
    def __init__(self, mock_response):
        self.mock_response = mock_response
        self.messages = self
    
    def create(self, **kwargs):
        return MagicMock(content=[MagicMock(text=self.mock_response)])

# Test directory
TEST_DIR = "/Users/meirsabag/Public/browser_use_ver4_newVersion/TEST/edge_case_tests"

# Standard mock data for testing
MOCK_JSON_DATA_STANDARD = """```json
[
  {
    "name": "Test Audience 1",
    "type": "Custom Audience",
    "availability": "Ready",
    "date_created": "01/01/2023",
    "audience_id": "123456789012345"
  },
  {
    "name": "Test Audience 2",
    "type": "Lookalike",
    "availability": "Ready",
    "date_created": "02/01/2023",
    "audience_id": "234567890123456"
  }
]
```"""

# Response with properly capitalized field names
MOCK_JSON_DATA_CAPITALIZED = """```json
[
  {
    "Name": "Test Audience 3",
    "Type": "Custom Audience",
    "Availability": "Ready",
    "Date created": "03/01/2023",
    "Audience ID": "345678901234567"
  },
  {
    "Name": "Test Audience 4",
    "Type": "Lookalike",
    "Availability": "Ready",
    "Date created": "04/01/2023",
    "Audience ID": "456789012345678"
  }
]
```"""

# Response wrapped in an object
MOCK_JSON_DATA_WRAPPED = """```json
{
  "audience_data": [
    {
      "name": "Test Audience 5",
      "type": "Custom Audience",
      "availability": "Ready",
      "date_created": "05/01/2023",
      "audience_id": "567890123456789"
    },
    {
      "name": "Test Audience 6",
      "type": "Lookalike",
      "availability": "Ready",
      "date_created": "06/01/2023",
      "audience_id": "678901234567890"
    }
  ]
}
```"""

# Response with missing fields
MOCK_JSON_DATA_MISSING_FIELDS = """```json
[
  {
    "name": "Test Audience 7",
    "type": "Custom Audience",
    "audience_id": "789012345678901"
  },
  {
    "name": "Test Audience 8",
    "availability": "Ready",
    "audience_id": "890123456789012"
  }
]
```"""

# Response with extra fields
MOCK_JSON_DATA_EXTRA_FIELDS = """```json
[
  {
    "name": "Test Audience 9",
    "type": "Custom Audience",
    "availability": "Ready",
    "date_created": "09/01/2023",
    "audience_id": "901234567890123",
    "size": "1,000,000+",
    "source": "Website",
    "description": "Test description"
  },
  {
    "name": "Test Audience 10",
    "type": "Lookalike",
    "availability": "Ready",
    "date_created": "10/01/2023",
    "audience_id": "012345678901234",
    "size": "500,000+",
    "retention": "30 days"
  }
]
```"""

# Setup and teardown functions
def setup_test_environment():
    """Set up the test environment by creating test directories and files"""
    # Ensure the test directory exists
    os.makedirs(TEST_DIR, exist_ok=True)
    
    # Ensure the agent-files directory exists (used by extract_audience_data)
    agent_files_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/agent-files"
    os.makedirs(agent_files_dir, exist_ok=True)

def teardown_test_environment():
    """Clean up the test environment by removing test directories and files"""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

async def mock_extract_audience_data(params, browser, mock_response, expected_output_path=None):
    """
    Run the extract_audience_data function with a mocked Claude API response.
    
    Args:
        params: ExtractAudienceDataAction parameters
        browser: MockBrowserContext instance
        mock_response: Mock JSON response from Claude
        expected_output_path: Optional path for expected output file
        
    Returns:
        Tuple of (ActionResult, output_path)
    """
    # Generate a unique output path if none provided
    if expected_output_path is None:
        test_id = str(uuid.uuid4())[:8]
        expected_output_path = os.path.join(TEST_DIR, f"test_output_{test_id}.json")
    
    # Ensure the directory for the output file exists
    os.makedirs(os.path.dirname(expected_output_path), exist_ok=True)
    
    # Create a patched anthropic client that returns the mock response
    mock_client = MockAnthropicClient(mock_response)
    
    # Patch the anthropic.Anthropic class to return our mock client
    with patch('anthropic.Anthropic', return_value=mock_client):
        # Set the file path in the parameters if not the first run
        if not params.is_first_run and not params.file_path:
            params = ExtractAudienceDataAction(
                is_first_run=params.is_first_run,
                file_path=expected_output_path
            )
        
        # Run the extract_audience_data function
        result = await extract_audience_data(params, browser)
        
        # If it's the first run, extract the file path from the success message
        if params.is_first_run and result.extracted_content:
            # Extract file path from the message using regex
            file_path_match = re.search(r'Saved to: (.*?)$', result.extracted_content)
            if file_path_match:
                expected_output_path = file_path_match.group(1)
        
        return result, expected_output_path

async def test_standard_format():
    """Test the function with standard JSON format response"""
    # Setup
    browser = MockBrowserContext()
    params = ExtractAudienceDataAction(is_first_run=True)
    
    # Run the test
    result, output_path = await mock_extract_audience_data(params, browser, MOCK_JSON_DATA_STANDARD)
    
    # Verify the result
    assert not result.error, f"Error: {result.error}"
    assert "Successfully extracted audience data" in result.extracted_content
    
    # Verify the output file
    with open(output_path, 'r') as f:
        data = json.load(f)
        
    # Check that we have the expected number of entries
    assert len(data) == 2, f"Expected 2 entries, got {len(data)}"
    
    # Check that field names are properly capitalized
    assert "Name" in data[0]
    assert "Type" in data[0]
    assert "Availability" in data[0]
    assert "Date created" in data[0]
    assert "Audience ID" in data[0]
    
    print("✅ Standard format test passed")
    return output_path

async def test_append_with_duplicates(first_run_output):
    """Test appending to an existing file with duplicate audience IDs"""
    # Setup
    browser = MockBrowserContext()
    params = ExtractAudienceDataAction(
        is_first_run=False,
        file_path=first_run_output
    )
    
    # Create a modified version of the second data set with one duplicate ID and one new ID
    duplicate_data = """```json
[
  {
    "name": "Test Audience 3",
    "type": "Custom Audience",
    "availability": "Ready",
    "date_created": "03/01/2023",
    "audience_id": "123456789012345"
  },
  {
    "name": "Test Audience 4",
    "type": "Lookalike",
    "availability": "Ready",
    "date_created": "04/01/2023",
    "audience_id": "345678901234567"
  }
]
```"""
    
    # Run the test
    result, output_path = await mock_extract_audience_data(params, browser, duplicate_data, first_run_output)
    
    # Verify the result
    assert not result.error, f"Error: {result.error}"
    
    # Verify the output file
    with open(output_path, 'r') as f:
        data = json.load(f)
    
    # We should now have 3 entries (2 from first run + 1 new one)
    # The 1 duplicate should be skipped
    assert len(data) == 3, f"Expected 3 entries after deduplication, got {len(data)}"
    
    # Check for duplicates by audience ID
    audience_ids = [entry.get("Audience ID") for entry in data]
    assert len(audience_ids) == len(set(audience_ids)), "Duplicate audience IDs found"
    
    print("✅ Append with duplicates test passed")
    return output_path

async def test_different_response_formats():
    """Test handling different response formats from Claude"""
    formats = {
        "wrapped": MOCK_JSON_DATA_WRAPPED,
        "capitalized": MOCK_JSON_DATA_CAPITALIZED,
        "missing_fields": MOCK_JSON_DATA_MISSING_FIELDS,
        "extra_fields": MOCK_JSON_DATA_EXTRA_FIELDS
    }
    
    for format_name, mock_data in formats.items():
        # Setup
        browser = MockBrowserContext()
        params = ExtractAudienceDataAction(is_first_run=True)
        
        # Run the test
        result, output_path = await mock_extract_audience_data(params, browser, mock_data)
        
        # Verify the result
        assert not result.error, f"Error in {format_name} format: {result.error}"
        
        # Verify the output file
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        # Check that entries exist and have expected fields
        assert len(data) > 0, f"No entries found for {format_name} format"
        
        # Check field names are properly capitalized
        assert all("Name" in entry for entry in data), f"Name field missing in {format_name} format"
        assert all("Audience ID" in entry for entry in data), f"Audience ID field missing in {format_name} format"
        
        print(f"✅ {format_name} format test passed")

async def test_empty_file():
    """Test appending to an empty valid JSON file"""
    # Create an empty JSON file with an empty array
    empty_file_path = os.path.join(TEST_DIR, "empty_file.json")
    with open(empty_file_path, 'w') as f:
        f.write("[]")
    
    # Setup
    browser = MockBrowserContext()
    params = ExtractAudienceDataAction(
        is_first_run=False,
        file_path=empty_file_path
    )
    
    # Run the test
    result, output_path = await mock_extract_audience_data(params, browser, MOCK_JSON_DATA_STANDARD, empty_file_path)
    
    # Verify the result
    assert not result.error, f"Error: {result.error}"
    
    # Verify the output file
    with open(output_path, 'r') as f:
        data = json.load(f)
    
    # We should have 2 entries
    assert len(data) == 2, f"Expected 2 entries, got {len(data)}"
    
    print("✅ Empty file test passed")

async def test_malformed_json_file():
    """Test handling a malformed JSON file when appending"""
    # Create a malformed JSON file
    malformed_file_path = os.path.join(TEST_DIR, "malformed_file.json")
    with open(malformed_file_path, 'w') as f:
        f.write("{not valid json")
    
    # Setup
    browser = MockBrowserContext()
    params = ExtractAudienceDataAction(
        is_first_run=False,
        file_path=malformed_file_path
    )
    
    # Run the test
    result, output_path = await mock_extract_audience_data(params, browser, MOCK_JSON_DATA_STANDARD, malformed_file_path)
    
    # Verify the result - should have an error
    assert result.error, "Expected an error for malformed JSON file but got success"
    
    print("✅ Malformed JSON file test passed")

async def main():
    """Run all the tests"""
    try:
        # Setup test environment
        setup_test_environment()
        
        print("Testing various edge cases for the extract_audience_data function")
        
        # Run tests in sequence
        first_run_output = await test_standard_format()
        await test_append_with_duplicates(first_run_output)
        await test_different_response_formats()
        await test_empty_file()
        await test_malformed_json_file()
        
        print("\nAll tests completed successfully!")
        
    finally:
        # Keep the test output for inspection
        print(f"Test output files preserved at: {TEST_DIR}")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(main()) 