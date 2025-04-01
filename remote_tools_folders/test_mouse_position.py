"""
Test script for the mouse positioning functionality.
"""

import asyncio
from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig
from custom_controller import controller
from langchain_anthropic import ChatAnthropic

async def test_mouse_positioning():
    """
    Test the mouse positioning functionality by moving the mouse cursor
    to different positions on the page and performing hover actions.
    """
    llm = ChatAnthropic(model="claude-3-7-sonnet-20250219")
    
    browser = Browser(config=BrowserConfig(
        headless=False,  # Set to False to see the browser window
    ))
    
    try:
        # Define a comprehensive task that demonstrates all mouse capabilities
        task = """
        Go to https://www.example.com and demonstrate the mouse positioning and wheel functionality by completing these tasks:

        PART 1: Basic Mouse Positioning
        1. Move the mouse cursor to the middle of the page (coordinates around 300, 300)
        2. Move the mouse cursor to the top-right corner (coordinates around 500, 100)
        3. Move the mouse cursor to the bottom-left corner (coordinates around 100, 500)
        
        PART 2: Demonstrate Different Scroll Patterns
        4. Small precise scroll: Scroll down the page by 150 pixels using the mouse wheel
        5. Wait for 1 second to observe any content loading
        6. Medium scroll: Continue scrolling down by 300 more pixels
        7. Wait for 1 second to observe any content loading
        8. Large scroll: Continue scrolling down by 600 more pixels to quickly reach the bottom
        9. Wait for 1 second
        
        PART 3: Scrolling in Different Directions
        10. Scroll up by 200 pixels to return to a previous position
        11. Wait for 1 second
        12. Try horizontal scrolling: first position the mouse in the middle of the page, then scroll right by 100 pixels
        13. Scroll left by 100 pixels to return to the original position
        
        PART 4: Natural Scrolling Pattern
        14. Perform a natural scrolling pattern by:
           a. Scrolling down by 200 pixels
           b. Waiting 1 second for content to load
           c. Scrolling down by another 200 pixels
           d. Waiting 1 second for content to load
           e. Scrolling down by another 200 pixels
        
        This comprehensive test demonstrates all the mouse positioning and wheel functionality,
        including both vertical and horizontal scrolling with various amounts and patterns.
        """
        
        # Create and run the agent with our custom controller
        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            controller=controller,
        )
        
        result = await agent.run()
        print("Test Result:")
        print(result)
        
    except Exception as e:
        print(f"Test Error: {str(e)}")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_mouse_positioning()) 