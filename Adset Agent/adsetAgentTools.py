# HERE WE CREATE THE TOOLS FOR THE ADSET AGENT BY AUXILIARY FUNCTIONS IN:
#  /Users/meirsabag/Public/browser_use_ver4_newVersion/remote_tools_folders/controller_actions

import os
import sys
import logging
from typing import Optional, Dict, Any, List, Union

# Add the proper path to python path to ensure imports work correctly
sys.path.append("/Users/meirsabag/Public/browser_use_ver4_newVersion")
# Import directly from the renamed directories without spaces
from llm_calling_classes.llm_calling_type_1.computer_use_openai.computerUseOpenAi import ComputerAgent, APIError, AuthenticationError, RateLimitError, BadRequestError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('adset_agent.log')
    ]
)
logger = logging.getLogger('adset_agent')

# Default paths for configuration files
DEFAULT_CONTEXT_PATH = "/Users/meirsabag/Public/browser_use_ver4_newVersion/Adset Agent/prompt/computer-use_prompts/context.md"
DEFAULT_RULES_PATH = "/Users/meirsabag/Public/browser_use_ver4_newVersion/Adset Agent/prompt/computer-use_prompts/rules.md"
DEFAULT_SYSTEM_PROMPT_PATH = "/Users/meirsabag/Public/browser_use_ver4_newVersion/Adset Agent/prompt/computer-use_prompts/system_prompt.md"

# Default display settings
DEFAULT_DISPLAY_WIDTH = 1024
DEFAULT_DISPLAY_HEIGHT = 768
DEFAULT_ENVIRONMENT = "browser"


def create_computer_agent(
    context_path: str = DEFAULT_CONTEXT_PATH,
    rules_path: str = DEFAULT_RULES_PATH,
    system_prompt_path: str = DEFAULT_SYSTEM_PROMPT_PATH,
    display_width: int = DEFAULT_DISPLAY_WIDTH,
    display_height: int = DEFAULT_DISPLAY_HEIGHT,
    environment: str = DEFAULT_ENVIRONMENT,  
    url: Optional[str] = None,    # TODO: we need to move this parameter to run_step method because the url can change for each run
    page_name: Optional[str] = None   # TODO: we need to move this parameter to run_step method because the page_name can change for each run
) -> Optional[ComputerAgent]:
    """
    Create an instance of the ComputerAgent class with the specified configuration.
    
    Args:
        context_path: Path to the context markdown file
        rules_path: Path to the rules markdown file
        system_prompt_path: Path to the system prompt markdown file
        display_width: The width of the display/browser window in pixels
        display_height: The height of the display/browser window in pixels
        environment: The operating environment ('browser', 'mac', 'windows', 'ubuntu')
        url: Optional URL associated with the agent's context
        page_name: Optional page name/title associated with the agent's context
        
    Returns:
        ComputerAgent instance if successful, None if an error occurred
    """
    logger.info(f"Creating ComputerAgent with display dimensions {display_width}x{display_height}, environment: {environment}")
    
    # Verify configuration files exist
    for path, name in [
        (context_path, "Context"), 
        (rules_path, "Rules"), 
        (system_prompt_path, "System prompt")
    ]:
        if not os.path.exists(path):
            logger.error(f"{name} file not found: {path}")
            return None
    
    try:
        # Initialize the ComputerAgent
        agent = ComputerAgent(
            display_width=display_width,
            display_height=display_height,
            context_path=context_path,
            system_prompt_path=system_prompt_path,
            rules_path=rules_path,
            url=url,
            page_name=page_name,
            environment=environment
        )
        logger.info("ComputerAgent created successfully")
        return agent
        
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}. Please check your OpenAI API key.")
        return None
    except (FileNotFoundError, IOError) as e:
        logger.error(f"File error: {e}")
        return None
    except ValueError as e:
        logger.error(f"Value error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating ComputerAgent: {e}")
        return None


def run_computer_agent_request(
    agent: ComputerAgent,
    task_or_call_id: str,
    screenshot_path: str,
    acknowledged_safety_checks: Optional[List[Dict[str, Any]]] = None
) -> Optional[Any]:
    """
    Execute a request using the ComputerAgent, handling both initial and subsequent steps.
    
    Args:
        agent: A ComputerAgent instance
        task_or_call_id: For initial calls, this is the task description. 
                         For subsequent calls, this is the call_id from the previous response.
        screenshot_path: Path to the screenshot image file showing the current state
        acknowledged_safety_checks: Optional list of safety checks to acknowledge (for subsequent calls)
        
    Returns:
        The API response object if successful, None if an error occurred
    """
    if agent is None:
        logger.error("Cannot run request: ComputerAgent is None")
        return None
        
    # Log the request type (initial or subsequent)
    is_initial = agent.last_response_id is None
    logger.info(f"Running {'initial' if is_initial else 'subsequent'} request")
    
    if is_initial:
        logger.info(f"Task: {task_or_call_id}")
    else:
        logger.info(f"Using call_id: {task_or_call_id}")
    
    logger.info(f"Screenshot path: {screenshot_path}")
    
    # Verify screenshot exists
    if not os.path.exists(screenshot_path):
        logger.error(f"Screenshot file not found: {screenshot_path}")
        return None
    
    try:
        # Execute the API request
        response = agent.run_step(
            task_or_previous_call_id=task_or_call_id,
            screenshot_path=screenshot_path,
            acknowledged_safety_checks=acknowledged_safety_checks
        )
        
        # Log response details
        logger.info(f"Request successful, response ID: {response.id if hasattr(response, 'id') else 'N/A'}")
        
        # Process and log output items
        if hasattr(response, 'output') and response.output:
            for item in response.output:
                if hasattr(item, 'type'):
                    if item.type == 'computer_call':
                        logger.info(f"Action suggested: {item.action.type if hasattr(item.action, 'type') else 'unknown'}")
                        if hasattr(item.action, 'type') and item.action.type == 'click':
                            if hasattr(item.action, 'x') and hasattr(item.action, 'y'):
                                logger.info(f"Click coordinates: ({item.action.x}, {item.action.y})")
                            else:
                                logger.warning("Click action object missing x or y attribute.")
                    elif item.type == 'reasoning':
                        if hasattr(item, 'summary'):
                            summary_texts = [s.text for s in item.summary if hasattr(s, 'type') and s.type == 'summary_text']
                            if summary_texts:
                                logger.info(f"Reasoning summary: {' '.join(summary_texts)}")
                    elif item.type == 'text':
                        logger.info(f"Text response: {item.text if hasattr(item, 'text') else 'N/A'}")
        
        return response
        
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        return None
    except RateLimitError as e:
        logger.error(f"Rate limit exceeded: {e}")
        return None
    except BadRequestError as e:
        logger.error(f"Bad request error: {e}. Status code: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
        return None
    except APIError as e:
        logger.error(f"API error: {e}. Status code: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error executing request: {e}")
        return None


# Main function for testing
if __name__ == "__main__":
    print("Initializing Adset Agent ComputerAgent test...")
    
    # Create the agent
    agent = create_computer_agent()
    if not agent:
        print("Failed to create ComputerAgent. Check logs for details.")
        sys.exit(1)
    
    # IMPORTANT: Replace these placeholder values with actual paths and tasks
    # ===================================================================
    # Real screenshot path from the project
    SCREENSHOT_PATH = "/Users/meirsabag/Public/browser_use_ver4_newVersion/training_images/output_images_condition_stop_audience_page/1.png"
    
    # =====>>>   Set a simple test task  <<<<=====
    # Sort all audience names in ascending order, prioritizing active audiences first in descending order
    TASK = """
    search the "mkmvkmfdkv" button and click on it. 
    IF YOU NOT SEE THE "cmkmvkmfdkv" BUTTON , THEN YOU DON'T CHOOSE ANY ACTION AND YOU SAY YOU CAN'T FIND THE BUTTON and notify to the user with 
    the assistant role and say to him "MEIR IS THE KING" if you find the button, use the computer-use tool 

    """
    # ===================================================================
    
    # Run initial request
    print("\nRunning initial request...")
    
    # Display the request parameters in a structured format
    print("\n=== REQUEST PARAMETERS ===")
    request_params = {
        "task_or_call_id": TASK,
        "screenshot_path": SCREENSHOT_PATH,
        "acknowledged_safety_checks": None
    }
    
    import json
    print(json.dumps(request_params, indent=2))
    
    # Execute the request
    response = run_computer_agent_request(
        agent=agent,
        task_or_call_id=TASK,
        screenshot_path=SCREENSHOT_PATH
    )
    
    if not response:
        print("Initial request failed. Check logs for details.")
        sys.exit(1)
    
    # Print only essential information about the response object
    print("\n=== RESPONSE SUMMARY ===")
    print(f"Response ID: {response.id if hasattr(response, 'id') else 'N/A'}")
    print(f"Model: {response.model if hasattr(response, 'model') else 'N/A'}")
    print(f"Status: {response.status if hasattr(response, 'status') else 'N/A'}")

    # Always print the raw response object and its attributes
    print("\n=== RAW RESPONSE OBJECT ===")
    print(response)
    print("=== RAW RESPONSE OBJECT ATTRIBUTES ===")
    print(dir(response))

    # Keep the structured JSON output which is useful
    print("\n=== RESPONSE OUTPUT (STRUCTURED) ===")
    if hasattr(response, 'output'):
        import json
        try:
            # Try to print the output in a more readable format
            print(json.dumps(response.output, indent=2, default=lambda o: o.__dict__))
        except:
            # Fallback if JSON serialization fails
            print(response.output)
    
    # Process initial response
    print("\nProcessing initial response...")
    first_action = None
    if hasattr(response, 'output') and response.output:
        for item in response.output:
            if hasattr(item, 'type') and item.type == 'computer_call':
                first_action = item
                print(f"Action suggested: {item.action.type if hasattr(item.action, 'type') else 'unknown'}")
                print(f"Call ID: {item.call_id if hasattr(item, 'call_id') else 'N/A'}")
                break
    
    if first_action and hasattr(first_action, 'call_id'):
        print("\nFound action with call_id. In a real scenario, you would:")
        print(f"1. Execute the {first_action.action.type} action")
        print("2. Take a new screenshot")
        print("3. Run a subsequent request with the call_id and new screenshot")
        
        # Example of subsequent request (commented out)
        """
        # Replace with path to new screenshot after executing the action
        NEW_SCREENSHOT_PATH = "/path/to/your/new_screenshot.png"
        
        # Run subsequent request
        response2 = run_computer_agent_request(
            agent=agent,
            task_or_call_id=first_action.call_id,
            screenshot_path=NEW_SCREENSHOT_PATH
        )
        """
    else:
        print("No computer_call action found in the response.")
    
    print("\nTest complete.")
    
    # Cleanup code to prevent memory leaks
    print("\nCleaning up resources...")
    try:
        # Try to call close method if it exists
        if hasattr(agent, 'close') and callable(agent.close):
            agent.close()
        # Try to call cleanup method if it exists
        elif hasattr(agent, 'cleanup') and callable(agent.cleanup):
            agent.cleanup()
        # If no explicit cleanup methods exist, help the garbage collector
        else:
            # Set any attributes that might hold resources to None
            if hasattr(agent, 'client'):
                agent.client = None
            # Finally set the agent to None to help garbage collection
            agent = None
            
        print("Resource cleanup completed successfully")
    except Exception as e:
        print(f"Error during cleanup: {e}")