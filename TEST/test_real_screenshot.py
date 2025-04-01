"""
Test file for the extract_audience_data function using a real screenshot.
"""

import os
import sys
import json
import base64
import asyncio
from dotenv import load_dotenv
import re

# Add the project root directory to the Python path
sys.path.append("/Users/meirsabag/Public/browser_use_ver4_newVersion")

# Import the custom controller
from remote_tools_folders.custom_controller import extract_audience_data, ExtractAudienceDataAction
from browser_use.agent.views import ActionResult

class MockBrowserContext:
    """A mock browser context for testing purposes"""
    def __init__(self, screenshot_data):
        self.screenshot_data = screenshot_data
        
    async def get_current_page(self):
        return None
        
    async def take_screenshot(self, full_page=False):
        """Return the predefined screenshot data"""
        return self.screenshot_data

def load_image_as_base64(image_path):
    """
    Load an image file and convert it to base64 encoding.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        base64 encoded string of the image
    """
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        base64_data = base64.b64encode(image_data).decode("utf-8")
        return base64_data

async def test_extract_audience_data_with_real_screenshot():
    """Test extracting audience data from a real screenshot"""
    # Load environment variables
    load_dotenv()
    
    # Path to the real screenshot
    screenshot_path = "/Users/meirsabag/Public/browser_use_ver4_newVersion/Screenshot 2025-03-19 at 16.44.15.png"
    
    # Ensure the screenshot exists
    if not os.path.exists(screenshot_path):
        print(f"ERROR: Screenshot not found at {screenshot_path}")
        return
    
    print(f"Loading screenshot from: {screenshot_path}")
    
    # Load the image as base64
    try:
        base64_image = load_image_as_base64(screenshot_path)
        print(f"Successfully loaded image ({len(base64_image)} characters in base64)")
        if base64_image.startswith("iVBORw0KGgo"):
            print("Detected PNG image format")
        else:
            print("Image format not detected as PNG")
    except Exception as e:
        print(f"ERROR loading image: {str(e)}")
        return
    
    # Test output directory
    test_output_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/TEST/output"
    os.makedirs(test_output_dir, exist_ok=True)
    
    # Create test output file path
    output_file_path = os.path.join(test_output_dir, "real_screenshot_results.json")
    
    # Create parameters (no screenshot_data parameter needed anymore)
    params = ExtractAudienceDataAction(
        is_first_run=True
    )
    
    # Create a mock browser context with our screenshot data
    browser = MockBrowserContext(base64_image)
    
    # Call the function
    print("\nTesting extract_audience_data with real screenshot...")
    try:
        result = await extract_audience_data(params, browser)
        
        # Check result and display extracted data
        if result.error:
            print(f"ERROR: {result.error}")
        else:
            print(f"SUCCESS: {result.extracted_content}")
            
            # Extract file path from the success message
            # Pattern to match the file path in the success message
            file_path_match = re.search(r'Saved to: (.+\.json)', result.extracted_content)
            
            if file_path_match:
                actual_output_path = file_path_match.group(1)
                print(f"Extracted file path: {actual_output_path}")
                
                # Try to read the output file using the extracted path
                try:
                    with open(actual_output_path, 'r') as f:
                        audience_data = json.load(f)
                        
                    # Print the first few entries as verification
                    print(f"Extracted {len(audience_data)} audience entries")
                    if audience_data:
                        print("\nFirst 5 entries:")
                        for i, entry in enumerate(audience_data[:5]):
                            print(f"  {i+1}. Name: {entry.get('Name', 'N/A')}, Type: {entry.get('Type', 'N/A')}, " 
                                f"Availability: {entry.get('Availability', 'N/A')}, Audience ID: {entry.get('Audience ID', 'N/A')}")
                except FileNotFoundError:
                    print(f"File not found at: {actual_output_path}")
                except json.JSONDecodeError:
                    print(f"Error parsing JSON from file: {actual_output_path}")
                except Exception as e:
                    print(f"Error reading output file: {str(e)}")
            else:
                print("Could not extract file path from success message")
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")

async def main():
    """Run the tests"""
    await test_extract_audience_data_with_real_screenshot()

if __name__ == "__main__":
    # Run the tests
    asyncio.run(main()) 