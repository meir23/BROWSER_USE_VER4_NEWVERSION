@controller.action(
    'Scroll page using mouse wheel',
    param_model=MouseWheelAction
)
async def mouse_wheel(params: MouseWheelAction, browser: BrowserContext) -> ActionResult:
    """
    Scroll the page using mouse wheel simulation. This function emulates a user scrolling with their physical mouse wheel.
    
    PARAMETER USAGE GUIDE:
    
    delta_y (vertical scrolling):
        - POSITIVE values (e.g. 300) = scroll DOWN the page
        - NEGATIVE values (e.g. -200) = scroll UP the page
        
    
    delta_x (horizontal scrolling):
        - POSITIVE values (e.g. 100) = scroll RIGHT
        - NEGATIVE values (e.g. -100) = scroll LEFT
        - Typically use 0 for normal vertical-only scrolling
        - Use non-zero values only for:
          * Horizontally scrollable containers/carousels
          * Wide tables or spreadsheets
          * Maps or horizontal timelines
          * Mobile-style horizontal navigation
    
    WHEN TO USE THIS FUNCTION:
    
    1. Natural scrolling behavior: Use when you need to simulate real user scrolling (triggers scroll events)
    2. Hover-dependent UI: When scrolling might reveal hover-sensitive elements
    3. Lazy-loading content: When content loads as you scroll (social media feeds, infinite scroll pages)
    4. Precise scroll control: When exact positioning is needed to reveal specific elements
    5. Horizontal scrolling: For interfaces with horizontal scroll components
    
    USAGE TIPS:
    
    - Chain multiple small scrolls rather than one large scroll to simulate natural behavior
    - Combine with mouse positioning before/after scrolling
    - Allow small pauses between scrolls to let content load
    - For infinite scrolling pages, use repeated smaller scrolls (300-500px) with pauses
    - For horizontal scrolling elements, first position the mouse over the element, then use delta_x
    
    Args:
        params: MouseWheelAction with delta_x and delta_y values
        browser: Browser context instance
    
    Returns:
        ActionResult: Result of the action with confirmation message
    """
    try:
        page = await browser.get_current_page()
        await page.mouse.wheel(params.delta_x, params.delta_y)
        
        # Wait for network idle
        await page.wait_for_load_state('networkidle', timeout=5000)
        
        # Create appropriate message based on scroll direction
        horizontal_msg = f"{abs(params.delta_x)} pixels {'right' if params.delta_x > 0 else 'left'}" if params.delta_x != 0 else ""
        vertical_msg = f"{abs(params.delta_y)} pixels {'down' if params.delta_y > 0 else 'up'}" if params.delta_y != 0 else ""
        
        if horizontal_msg and vertical_msg:
            scroll_msg = f"{horizontal_msg} and {vertical_msg}"
        else:
            scroll_msg = horizontal_msg or vertical_msg
            
        message = f"🖱️ Scrolled {scroll_msg} using mouse wheel"
        return ActionResult(extracted_content=message, include_in_memory=True)
    except Exception as e:
        error_message = f"Failed to scroll using mouse wheel: {str(e)}"
        return ActionResult(error=error_message)