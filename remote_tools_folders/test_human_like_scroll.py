"""
Test the human-like scrolling functionality in the custom_controller.
"""

import asyncio
import os
import sys
from pathlib import Path

# Adjust path to import from parent directory
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from remote_tools_folders.custom_controller import mouse_wheel, MouseWheelAction
from browser_use.browser.context import BrowserContext
from playwright.async_api import async_playwright

# A simpler approach that doesn't rely on BrowserContext
async def test_human_like_scrolling():
    """
    Test the human-like scrolling by opening a test site and performing scrolls.
    """
    print("Starting human-like scrolling test...")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # Use headless=False to see the scrolling visually
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()
        
        # Create a simple mock browser context
        class SimpleBrowserContext:
            async def get_current_page(self):
                return page
        
        browser_ctx = SimpleBrowserContext()
        
        # Navigate to a test site with scrollable content
        await page.goto("https://news.ycombinator.com/", wait_until="domcontentloaded")
        
        print("Page loaded. Starting scroll operations...")
        
        # Create parameters for scrolling down
        params = MouseWheelAction(delta_x=0, delta_y=800)
        
        # Execute the human-like scrolling
        result = await mouse_wheel(params, browser_ctx)
        # Display full result object for inspection
        print(f"Down scroll - Full result: {result}")
        print(f"Down scroll - Result fields: extracted_content={result.extracted_content}, error={result.error}")
        
        # Wait a moment to see the effect
        await asyncio.sleep(3)
        
        # Scroll back up
        params = MouseWheelAction(delta_x=0, delta_y=-400)
        result = await mouse_wheel(params, browser_ctx)
        print(f"Up scroll - Full result: {result}")
        print(f"Up scroll - Result fields: extracted_content={result.extracted_content}, error={result.error}")
        
        # Wait a moment to see the effect
        await asyncio.sleep(3)
        
        # Test horizontal scrolling on a different site
        await page.goto("https://caniuse.com/", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        # Scroll horizontally
        params = MouseWheelAction(delta_x=300, delta_y=0)
        result = await mouse_wheel(params, browser_ctx)
        print(f"Horizontal scroll - Full result: {result}")
        print(f"Horizontal scroll - Result fields: extracted_content={result.extracted_content}, error={result.error}")
        
        # Wait a moment to see the effect
        await asyncio.sleep(5)
        
        # Close browser
        await browser.close()
        
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_human_like_scrolling()) 