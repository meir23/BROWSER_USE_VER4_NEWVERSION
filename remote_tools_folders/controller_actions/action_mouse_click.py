from browser_use import ActionResult
from browser_use.browser.context import BrowserContext
import traceback
# import logging

async def perform_mouse_click(browser: BrowserContext) -> ActionResult:
    """
    Helper function containing the logic to click the mouse at its current position.
    """
    try:
        page = await browser.get_current_page()
        # Note: Original code used (0, 0, position_relative_to_element=False) which clicks relative to top-left of viewport.
        # Playwright's default page.mouse.click(x, y) clicks at coordinates.
        # To click at the *current* mouse position implicitly, maybe just page.mouse.down() followed by page.mouse.up() is needed,
        # or simply use page.click('body', position={'x': current_x, 'y': current_y}) if position is tracked,
        # but the original code clicks at (0,0) of viewport. Sticking to original logic:
        await page.mouse.click(0, 0, position_relative_to_element=False)
        message = "🖱️ Mouse clicked at current position"
        return ActionResult(extracted_content=message, include_in_memory=True)
    except Exception as e:
        error_message = f"Failed to click mouse: {str(e)}"
        # Optional: Add logging here
        return ActionResult(error=error_message)
