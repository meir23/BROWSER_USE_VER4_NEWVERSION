"""
Test file for the extract_audience_data function in the custom_controller.py
"""

import os
import sys
import json
import asyncio
from dotenv import load_dotenv

# Add the project root directory to the Python path
sys.path.append("/Users/meirsabag/Public/browser_use_ver4_newVersion")

# Import the custom controller
from remote_tools_folders.custom_controller import extract_audience_data, ExtractAudienceDataAction

# A dummy base64 image - this is just a placeholder and won't work with actual extraction
# In a real scenario, you would use an actual screenshot of a Facebook audience table
DUMMY_BASE64_IMG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

class MockBrowserContext:
    """A mock browser context for testing purposes"""
    async def get_current_page(self):
        return None

async def test_extract_audience_data_first_run():
    """Test creating a new file for audience data"""
    # Load environment variables
    load_dotenv()
    
    # Ensure output directory exists
    test_output_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/TEST/output"
    os.makedirs(test_output_dir, exist_ok=True)
    
    # Create parameters for the first run (create new file)
    params = ExtractAudienceDataAction(
        screenshot_data=DUMMY_BASE64_IMG,
        is_first_run=True
    )
    
    # Create a mock browser context
    browser = MockBrowserContext()
    
    # Call the function
    print("Testing extract_audience_data with is_first_run=True...")
    try:
        result = await extract_audience_data(params, browser)
        print(f"Result: {result}")
        
        # Check if the function executed successfully
        if result.error:
            print(f"Error: {result.error}")
        else:
            print(f"Success: {result.extracted_content}")
            if result.metadata and 'file_path' in result.metadata:
                print(f"File path: {result.metadata['file_path']}")
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

async def test_extract_audience_data_subsequent_run():
    """Test appending to an existing file"""
    # Use our sample file for testing
    sample_file_path = "/Users/meirsabag/Public/browser_use_ver4_newVersion/TEST/output/sample_audience_data.json"
    
    if not os.path.exists(sample_file_path):
        print(f"Sample file not found at {sample_file_path}. Skipping subsequent run test.")
        return
    
    # Create parameters for the subsequent run (append to existing file)
    params = ExtractAudienceDataAction(
        screenshot_data=DUMMY_BASE64_IMG,
        is_first_run=False,
        file_path=sample_file_path
    )
    
    # Create a mock browser context
    browser = MockBrowserContext()
    
    # Call the function
    print("\nTesting extract_audience_data with is_first_run=False...")
    try:
        result = await extract_audience_data(params, browser)
        print(f"Result: {result}")
        
        # Check if the function executed successfully
        if result.error:
            print(f"Error: {result.error}")
        else:
            print(f"Success: {result.extracted_content}")
            if result.metadata and 'file_path' in result.metadata:
                print(f"File path: {result.metadata['file_path']}")
                
            # Check if the file was updated with new content
            with open(sample_file_path, 'r', encoding='utf-8') as f:
                updated_data = json.load(f)
                print(f"Updated file has {len(updated_data)} entries")
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

async def main():
    """Run the tests"""
    # Test creating a new file
    await test_extract_audience_data_first_run()
    
    # Test appending to an existing file
    await test_extract_audience_data_subsequent_run()

if __name__ == "__main__":
    # Run the tests
    asyncio.run(main()) 