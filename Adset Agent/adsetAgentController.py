# HERE WE CREATE THE CONTROLLER WITH CUSTOM ACTIONS FOR THE ADSET AGENT

import os
import sys
import tempfile
import logging
from typing import Optional, Dict, Any, List

# Ensure adsetAgentTools can be imported
# Adjust this path if necessary based on your project structure
sys.path.append("/Users/meirsabag/Public/browser_use_ver4_newVersion")
sys.path.append("/Users/meirsabag/Public/browser_use_ver4_newVersion/Adset Agent")

from browser_use import Controller, ActionResult, Browser
from pydantic import BaseModel, Field
import json

# Import the functions and necessary types from adsetAgentTools
try:
    from adsetAgentTools import (
        create_computer_agent,
        run_computer_agent_request,
        ComputerAgent,  # Assuming ComputerAgent class is accessible
        APIError, AuthenticationError, RateLimitError, BadRequestError # Import Exceptions if specific handling is needed
    )
    # Import default paths/values if needed for Pydantic models
    from adsetAgentTools import (
        DEFAULT_CONTEXT_PATH, DEFAULT_RULES_PATH, DEFAULT_SYSTEM_PROMPT_PATH,
        DEFAULT_DISPLAY_WIDTH, DEFAULT_DISPLAY_HEIGHT, DEFAULT_ENVIRONMENT
    )
except ImportError as e:
    logging.error(f"Failed to import from adsetAgentTools: {e}. Ensure the path is correct.")
    # Define dummy functions/classes if import fails to prevent further NameErrors
    # This allows the rest of the file to be parsed, but actions will fail at runtime.
    def create_computer_agent(*args, **kwargs): raise ImportError("adsetAgentTools not found")
    def run_computer_agent_request(*args, **kwargs): raise ImportError("adsetAgentTools not found")
    class ComputerAgent: pass
    class APIError(Exception): pass
    class AuthenticationError(APIError): pass
    class RateLimitError(APIError): pass
    class BadRequestError(APIError): pass
    DEFAULT_CONTEXT_PATH = "Adset Agent/prompt/computer-use_prompts/context.md"
    DEFAULT_RULES_PATH = "Adset Agent/prompt/computer-use_prompts/rules.md"
    DEFAULT_SYSTEM_PROMPT_PATH = "Adset Agent/prompt/computer-use_prompts/system_prompt.md"
    DEFAULT_DISPLAY_WIDTH = 1024
    DEFAULT_DISPLAY_HEIGHT = 768
    DEFAULT_ENVIRONMENT = "browser"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Controller Setup ---
controller = Controller()

# --- State Management ---
# Store the created ComputerAgent instance globally within this module.
# NOTE: This approach is simple but might not be suitable if multiple
# agents using this controller run concurrently in the same process.
_computer_agent_instance: Optional[ComputerAgent] = None

# --- Pydantic Models for Parameters ---

class CreateAgentParams(BaseModel):
    context_path: str = Field(DEFAULT_CONTEXT_PATH, description="Path to the context markdown file")
    rules_path: str = Field(DEFAULT_RULES_PATH, description="Path to the rules markdown file")
    system_prompt_path: str = Field(DEFAULT_SYSTEM_PROMPT_PATH, description="Path to the system prompt markdown file")
    display_width: int = Field(DEFAULT_DISPLAY_WIDTH, description="The width of the display/browser window in pixels")
    display_height: int = Field(DEFAULT_DISPLAY_HEIGHT, description="The height of the display/browser window in pixels")
    environment: str = Field(DEFAULT_ENVIRONMENT, description="The operating environment ('browser', 'mac', 'windows', 'ubuntu')")
    url: Optional[str] = Field(None, description="Optional initial URL associated with the agent's context")
    page_name: Optional[str] = Field(None, description="Optional initial page name associated with the agent's context")

class RunRequestParams(BaseModel):
    task_or_call_id: str = Field(..., description="For initial calls, the task description. For subsequent calls, the call_id from the previous response.")
    acknowledged_safety_checks: Optional[List[Dict[str, Any]]] = Field(None, description="Optional list of safety checks to acknowledge (for subsequent calls)")
    # screenshot_path will be handled internally using the browser context

# --- Custom Actions ---

@controller.action(
    'Initialize the Computer Vision Agent',
    param_model=CreateAgentParams
)
async def initialize_computer_agent(params: CreateAgentParams, browser: Browser) -> ActionResult:
    """
    Initializes the secondary Computer Agent responsible for vision-based tasks.
    This agent provides coordinates for clicks and scrolls.
    Stores the agent instance for use with 'run_computer_vision_request'.
    """
    global _computer_agent_instance
    logger.info(f"Attempting to initialize ComputerAgent with params: {params.dict()}")

    # Potentially use browser context to get current URL/Title if needed
    current_url = await browser.page.evaluate("() => window.location.href")
    current_title = await browser.page.title()
    
    # Decide whether to use params.url/page_name or current browser state
    # For now, let's prioritize params if provided, otherwise use browser state.
    url_to_use = params.url if params.url is not None else current_url
    page_name_to_use = params.page_name if params.page_name is not None else current_title

    try:
        agent = create_computer_agent(
            context_path=params.context_path,
            rules_path=params.rules_path,
            system_prompt_path=params.system_prompt_path,
            display_width=params.display_width,
            display_height=params.display_height,
            environment=params.environment,
            url=url_to_use,
            page_name=page_name_to_use
        )

        if agent:
            _computer_agent_instance = agent
            logger.info("ComputerAgent initialized successfully.")
            # Return the specific success message as requested
            return ActionResult(result="You now have the capability to get the coordinates you need for various click and scroll actions. Always use me when needed via the 'run_computer_vision_request' action.")
        else:
            logger.error("create_computer_agent returned None.")
            return ActionResult(error="Failed to initialize the Computer Vision Agent. Check logs.")

    except (AuthenticationError, FileNotFoundError, ValueError) as e:
        logger.error(f"Error during ComputerAgent initialization: {e}")
        return ActionResult(error=f"Initialization Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during ComputerAgent initialization: {e}", exc_info=True)
        return ActionResult(error=f"Unexpected Initialization Error: {e}")

@controller.action(
    'Run Computer Vision Request',
    param_model=RunRequestParams
)
async def run_computer_vision_request(params: RunRequestParams, browser: Browser) -> ActionResult:
    """
    Takes a screenshot of the current page and sends it to the initialized
    Computer Vision Agent along with the task or previous call_id to get the next action/coordinates.
    Requires 'initialize_computer_agent' to be called first.
    """
    global _computer_agent_instance
    logger.info(f"Running computer vision request with task/call_id: {params.task_or_call_id}")

    if _computer_agent_instance is None:
        logger.error("Computer Vision Agent is not initialized. Call 'initialize_computer_agent' first.")
        return ActionResult(error="Computer Vision Agent not initialized. Please call 'initialize_computer_agent' first.")

    screenshot_path = None
    try:
        # 1. Take screenshot using browser context
        logger.info("Taking screenshot...")
        screenshot_bytes = await browser.page.screenshot()

        # 2. Save screenshot to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(screenshot_bytes)
            screenshot_path = temp_file.name
        logger.info(f"Screenshot saved temporarily to: {screenshot_path}")

        # 3. Call the original run_computer_agent_request function
        response = run_computer_agent_request(
            agent=_computer_agent_instance,
            task_or_call_id=params.task_or_call_id,
            screenshot_path=screenshot_path,
            acknowledged_safety_checks=params.acknowledged_safety_checks
        )

        # 4. Process the response
        if response:
            logger.info("Computer vision request successful.")
            # Return the response object formatted as text
            try:
                # Attempt to serialize the relevant parts, similar to adsetAgentTools example
                output_data = response.output if hasattr(response, 'output') else response
                response_text = json.dumps(output_data, indent=2, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else str(o))
            except Exception as json_err:
                 logger.warning(f"Could not serialize response output to JSON: {json_err}. Falling back to str().")
                 response_text = str(response) # Fallback to simple string representation

            return ActionResult(result=response_text)
        else:
            logger.error("run_computer_agent_request returned None.")
            return ActionResult(error="Computer vision request failed. Check logs.")

    except (APIError, BadRequestError, RateLimitError, AuthenticationError) as e:
         logger.error(f"API or Authentication error during vision request: {e}")
         return ActionResult(error=f"Computer Vision API Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during computer vision request: {e}", exc_info=True)
        return ActionResult(error=f"Unexpected error during vision request: {e}")
    finally:
        # 5. Clean up the temporary screenshot file
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                os.remove(screenshot_path)
                logger.info(f"Cleaned up temporary screenshot: {screenshot_path}")
            except OSError as e:
                logger.error(f"Error deleting temporary screenshot {screenshot_path}: {e}") 