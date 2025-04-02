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

@controller.action('Check if scrolling should continue or stop based on page analysis')
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