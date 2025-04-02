from browser_use import ActionResult
from browser_use.browser.context import BrowserContext
import traceback
# import logging

async def perform_mouse_hover(x: float, y: float, browser: BrowserContext) -> ActionResult:
    """
    Helper function containing the logic to perform a mouse hover action.
    """
    try:
        page = await browser.get_current_page()
        await page.mouse.move(x, y) # Hover is achieved by moving the mouse
        message = f"🖱️ Mouse hovering at coordinates ({x}, {y})"
        return ActionResult(extracted_content=message, include_in_memory=True)
    except Exception as e:
        error_message = f"Failed to hover mouse: {str(e)}"
        # Optional: Add logging here
        return ActionResult(error=error_message)
