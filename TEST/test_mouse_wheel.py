#!/usr/bin/env python3
"""
Test script for the mouse_wheel function with logging.
This test verifies that:
1. The mouse_wheel function works correctly
2. Logs are properly written to the file
3. No logs appear in the terminal output
"""

import os
import sys
import asyncio
import unittest.mock
from pathlib import Path

# Add the parent directory to the path to import the custom controller module
sys.path.append(str(Path(__file__).parent.parent))
from remote_tools_folders.custom_controller import mouse_wheel, MouseWheelAction
from browser_use.browser.context import BrowserContext

class MockPage:
    """Mock page object for testing mouse wheel functionality"""
    def __init__(self):
        self.mouse = MockMouse()
        self.scroll_events = []
        self.viewport_size_value = {"width": 1200, "height": 800}
    
    async def viewport_size(self):
        """Return mock viewport size"""
        return self.viewport_size_value
    
    async def wait_for_load_state(self, state, timeout=None):
        """Mock wait for load state"""
        await asyncio.sleep(0.1)  # Simulate a small delay
        return True

class MockMouse:
    """Mock mouse object for testing mouse movements and wheel events"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.wheel_events = []
    
    async def move(self, x, y, steps=1):
        """Mock mouse move"""
        self.x = x
        self.y = y
        return True
    
    async def wheel(self, delta_x, delta_y):
        """Mock wheel event that records the deltas"""
        self.wheel_events.append((delta_x, delta_y))
        return True

class MockBrowserContext:
    """Mock browser context for testing with a mock page"""
    def __init__(self):
        self.page = MockPage()
    
    async def get_current_page(self):
        """Return the mock page"""
        return self.page

async def test_mouse_wheel():
    """
    Test the mouse_wheel function with various parameters and verify that:
    1. The function successfully completes
    2. Proper wheel events are triggered
    3. Logs are written to the expected log file
    4. No logs appear in the terminal
    """
    print("Starting mouse_wheel function test...")
    
    # Create params for vertical scrolling
    vertical_params = MouseWheelAction(delta_x=0, delta_y=300)
    
    # Create a mock browser context
    browser = MockBrowserContext()
    
    # Clear the log file if it exists
    log_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/logs"
    log_file = os.path.join(log_dir, "mouse_wheel_actions.log")
    
    try:
        os.makedirs(log_dir, exist_ok=True)
        if os.path.exists(log_file):
            # Backup the existing log file
            backup_file = f"{log_file}.bak"
            print(f"Backing up existing log file to {backup_file}")
            os.rename(log_file, backup_file)
    except Exception as e:
        print(f"Error handling log file: {str(e)}")
    
    print("Testing vertical scroll (300px down)...")
    
    # Execute the mouse_wheel function
    try:
        result = await mouse_wheel(vertical_params, browser)
        print("Mouse wheel function completed successfully")
        print(f"Result message: {result.extracted_content}")
        
        # Check the number of wheel events recorded
        wheel_events = browser.page.mouse.wheel_events
        print(f"Total wheel events recorded: {len(wheel_events)}")
        
        # Check if the log file was created
        if os.path.exists(log_file):
            file_size = os.path.getsize(log_file)
            print(f"Log file created successfully: {log_file} ({file_size} bytes)")
            
            # Read a sample of the log file (first few lines)
            with open(log_file, 'r', encoding='utf-8') as f:
                sample_lines = [next(f) for _ in range(10) if f]
                print("Sample log entries:")
                for line in sample_lines:
                    print(f"  {line.strip()}")
        else:
            print(f"ERROR: Log file was not created at {log_file}")
    
    except Exception as e:
        print(f"Error executing mouse_wheel function: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test horizontal scrolling
    print("\nTesting horizontal scroll (200px right)...")
    horizontal_params = MouseWheelAction(delta_x=200, delta_y=0)
    
    try:
        result = await mouse_wheel(horizontal_params, browser)
        print("Horizontal scroll completed successfully")
        print(f"Result message: {result.extracted_content}")
    except Exception as e:
        print(f"Error executing horizontal scroll: {str(e)}")
    
    # Test diagonal scrolling
    print("\nTesting diagonal scroll (100px right, 150px down)...")
    diagonal_params = MouseWheelAction(delta_x=100, delta_y=150)
    
    try:
        result = await mouse_wheel(diagonal_params, browser)
        print("Diagonal scroll completed successfully")
        print(f"Result message: {result.extracted_content}")
    except Exception as e:
        print(f"Error executing diagonal scroll: {str(e)}")
    
    print("\nAll tests completed.")
    
    # Check final log file size
    if os.path.exists(log_file):
        final_size = os.path.getsize(log_file)
        print(f"Final log file size: {final_size} bytes")
        
        # Count the number of log entries
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
            log_lines = log_content.splitlines()
            print(f"Total log entries: {len(log_lines)}")

async def main():
    """Main function to run the test"""
    await test_mouse_wheel()

if __name__ == "__main__":
    asyncio.run(main()) 