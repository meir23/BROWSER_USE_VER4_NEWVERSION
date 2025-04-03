"""
Custom controller for Browser-Use with mouse positioning functionality.
"""

from browser_use import Controller, ActionResult
from browser_use.browser.context import BrowserContext
from pydantic import BaseModel, Field
from typing import Optional, List, Tuple
import random
import math
import asyncio
import base64
import datetime
import os
import logging
import traceback
import sys
import importlib.util

# --- Action Implementations ---
# Add the directory to sys.path for importing from a hyphenated directory
LLM_IMPORT_SUCCESS = False
try:
    # First try to import directly using a path-based approach
    module_path = os.path.join(os.path.dirname(__file__), "llm-call-audienceEdit-think-gemini", "llm_caller.py")
    if os.path.exists(module_path):
        module_name = "llm_caller"
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        llm_caller = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(llm_caller)
        generate = llm_caller.generate
        LLM_IMPORT_SUCCESS = True
        logging.info("Successfully imported 'generate' function from llm_caller.py")
    else:
        logging.error(f"Could not find llm_caller.py at path: {module_path}")
except Exception as import_error:
    logging.error(f"Failed to import 'generate' function: {import_error}")
    # Define a placeholder function if import fails to avoid NameError later
    def generate(*args, **kwargs):
        raise ImportError("LLM 'generate' function could not be imported.")

from .controller_actions.action_move_mouse import perform_move_mouse, MouseMoveAction
from .controller_actions.action_mouse_click import perform_mouse_click
from .controller_actions.action_mouse_hover import perform_mouse_hover
from .controller_actions.action_mouse_wheel import perform_mouse_wheel, MouseWheelAction
from .controller_actions.action_extract_audience_data import perform_extract_audience_data, ExtractAudienceDataAction
from .controller_actions.action_generate_custom_prompt import perform_generate_custom_prompt
from .controller_actions.action_check_condition_stop_page_wheel import perform_check_condition_stop_page_wheel

# Note: All helper functions have been moved to their respective implementation files

# Create a model for the mouse movement parameters
class MouseMoveAction(BaseModel):
    x: float = Field(..., description="X coordinate relative to the viewport in CSS pixels")
    y: float = Field(..., description="Y coordinate relative to the viewport in CSS pixels")
    steps: Optional[int] = Field(1, description="Number of intermediate steps for the movement (default: 1)")

# Create a model for the mouse wheel parameters
class MouseWheelAction(BaseModel):
    delta_x: float = Field(0, description="Pixels to scroll horizontally (positive for right, negative for left). For most websites, use 0 for vertical-only scrolling.")
    delta_y: float = Field(..., description="Pixels to scroll vertically (positive for down, negative for up). Typical values: 100-300 for small scrolls, 500-800 for larger scrolls.")

# Create a model for the Facebook audience extraction parameters
class ExtractAudienceDataAction(BaseModel):
    is_first_run: bool = Field(True, description="Whether this is the first run (create new file) or not (append to existing)")
    file_path: Optional[str] = Field(None, description="Path to the existing JSON file (only used if is_first_run=False)")

# Create a model for the 'think' action parameters
class ThinkActionParams(BaseModel):
    task_description: Optional[str] = Field(None, description="Optional task description or question for the LLM to guide its thinking based on the screenshot.")

# Initialize the controller
controller = Controller()

@controller.action(
    'Move mouse cursor to specific coordinates on the page',
    param_model=MouseMoveAction
)
async def move_mouse(params: MouseMoveAction, browser: BrowserContext) -> ActionResult:
    """
    Action definition: Move the mouse cursor to specific coordinates on the page.
    Calls the helper function perform_move_mouse for implementation.
    """
    return await perform_move_mouse(params, browser)

# Optional - add more mouse-related functions if needed

@controller.action('Click mouse at current position')
async def mouse_click(browser: BrowserContext) -> ActionResult:
    """
    Action definition: Click the mouse at its current position.
    Calls the helper function perform_mouse_click for implementation.
    """
    return await perform_mouse_click(browser)

@controller.action('Perform mouse hover at specific coordinates')
async def mouse_hover(x: float, y: float, browser: BrowserContext) -> ActionResult:
    """
    Action definition: Move the mouse to specified coordinates to perform a hover action.
    Calls the helper function perform_mouse_hover for implementation.
    """
    return await perform_mouse_hover(x, y, browser)

@controller.action(
    'Scroll page using mouse wheel',
    param_model=MouseWheelAction
)
async def mouse_wheel(params: MouseWheelAction, browser: BrowserContext) -> ActionResult:
    """ Action definition: Scroll page using mouse wheel simulation. """
    return await perform_mouse_wheel(params, browser)

@controller.action(
    'Extract Facebook audience data from table screenshot',
    param_model=ExtractAudienceDataAction
)
async def extract_audience_data(params: ExtractAudienceDataAction, browser: BrowserContext) -> ActionResult:
    """
    Extracts audience data from a Facebook dashboard table screenshot using Claude's Vision API.
    
    This function:
    1. Takes a screenshot of the current page
    2. Sends the screenshot to Claude for analysis via Vision API
    3. Creates a new JSON file or appends to an existing one based on is_first_run parameter
    4. Ensures no duplicate audience_id entries when appending
    
    Args:
        params: ExtractAudienceDataAction with file options
        browser: Browser context instance used to capture the screenshot
    
    Returns:
        ActionResult: Result of the action with confirmation message and file path
    """
    return await perform_extract_audience_data(params, browser)

@controller.action('Generate custom prompt for agent')
async def generate_custom_prompt(browser: BrowserContext) -> ActionResult:
    """
    DO NOT USE THIS ACTION.!!!!! 
    I REPEAT DO NOT USE THIS ACTION.!!!!! 
    IT IS NOT SUPPOSED TO BE USED BECAUSE THIS TOOL IS UNDER DEVELOPMENT AND NOT READY YET.
    
    Generate a custom prompt as an instruction for the agent's language model.
    This action should only be used when all stopping conditions have been met
    and the agent needs to perform actions beyond its current capabilities.
    
    Args:
        browser: Browser context instance
    
    Returns:
        ActionResult: Result containing the generated prompt
    """
    return await perform_generate_custom_prompt(browser)

@controller.action('Check if scrolling should continue or stop based on Audience ADSet facebook dashboard page')
async def check_condition_stop_page_wheel(browser: BrowserContext) -> ActionResult:
    """
    Analyzes the current page screenshot to determine whether to continue scrolling vertically
    or stop based on the condition of the scroll bar and visible content.
    
    This function:
    1. Takes a screenshot of the current page
    2. Loads training images for Claude Vision API context
    3. Sends the screenshot and training images to Claude for analysis
    4. Parses the response to determine if scrolling should continue or stop
    5. Returns the decision and appropriate scroll parameters if needed
    
    Args:
        browser: Browser context instance used to capture the screenshot
    
    Returns:
        ActionResult: Result containing the scroll decision (CONTINUE/STOP) and scroll parameter
                     if applicable, to help the agent decide whether to continue scrolling
    """
    return await perform_check_condition_stop_page_wheel(browser)

@controller.action(
    'Think: Analyze current page screenshot with LLM',
    param_model=ThinkActionParams
)
async def think(params: ThinkActionParams, browser: BrowserContext) -> ActionResult:
    """
    Takes a screenshot, saves it with a timestamp, and calls an LLM
    (via the imported 'generate' function) to analyze the visual content
    and potentially guide the next steps based on the provided task description.

    Args:
        params: ThinkActionParams containing an optional task_description.
        browser: Browser context instance used to capture the screenshot.

    Returns:
        ActionResult: Result containing the LLM's response text or an error message.
    """
    if not LLM_IMPORT_SUCCESS:
         return ActionResult(error="LLM 'generate' function could not be imported. Check logs and project structure.")

    try:
        # 1. Define save directory (using the exact path provided)
        save_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/training_images/output_images_condition_stop_audience_page"
        os.makedirs(save_dir, exist_ok=True)
        logging.info(f"Ensured directory exists: {save_dir}")

        # 2. Generate timestamped filename (human-readable as requested)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(save_dir, f"think_screenshot_{timestamp}.png")

        # 3. Take screenshot
        logging.info("Taking screenshot for think action...")
        screenshot_bytes = await browser.page.screenshot()
        logging.info(f"Screenshot taken, size: {len(screenshot_bytes)} bytes")

        # 4. Save screenshot
        logging.info(f"Saving screenshot to: {file_path}")
        with open(file_path, "wb") as f:
            f.write(screenshot_bytes)
        logging.info("Screenshot saved successfully.")

        # 5. Prepare prompt for LLM
        prompt_text = params.task_description if params.task_description else "Analyze the provided screenshot of the webpage. Based on the visual context, describe the current state and suggest the most logical next step or action to take to accomplish standard web automation goals."
        logging.info(f"Prepared prompt for LLM (truncated): {prompt_text[:100]}...")

        # 6. Call LLM function (run synchronous function in thread)
        logging.info(f"Calling LLM function 'generate' with image: {file_path}")

        # Create a wrapper function that can be executed in a thread
        def run_generate():
            return generate(user_image_path=file_path, user_text=prompt_text)
            
        # Use asyncio.to_thread to run the synchronous 'generate' function
        # without blocking the main async event loop.
        llm_response = await asyncio.to_thread(run_generate)
        logging.info("LLM function 'generate' completed.")

        # Check if llm_response is None (indicating an error in 'generate') or empty
        if llm_response is None:
             logging.error("LLM generate function returned None, indicating an error occurred.")
             return ActionResult(error="LLM analysis failed. Check the logs of the llm_caller script.")
        elif not llm_response.strip():
             logging.warning("LLM generate function returned an empty response.")
             llm_response = "[LLM provided an empty response]"
        else:
            logging.info(f"LLM Response received (truncated): {llm_response[:100]}...")

        # 7. Return result in ActionResult
        result_message = f"LLM thought process complete using screenshot '{os.path.basename(file_path)}'.\nLLM Response:\n{llm_response}"
        return ActionResult(result=result_message)

    except FileNotFoundError as e:
         logging.error(f"Error saving or accessing screenshot file: {e}\n{traceback.format_exc()}")
         return ActionResult(error=f"File operation error during think action: {e}")
    except ImportError as e: # Catch potential import error if placeholder was called
        logging.error(f"ImportError during think action execution: {e}\n{traceback.format_exc()}")
        return ActionResult(error=f"LLM module import error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during think action: {e}\n{traceback.format_exc()}")
        return ActionResult(error=f"An unexpected error occurred during the think action: {e}")