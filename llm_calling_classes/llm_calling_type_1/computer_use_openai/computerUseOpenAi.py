import base64
import os
import time # Potentially useful for delays if needed
from openai import OpenAI, APIError, RateLimitError, AuthenticationError, BadRequestError

class ComputerAgent:
    """
    Manages interactions with the OpenAI Computer Use API (computer-use-preview model)
    for automating tasks based on visual context (screenshots).

    This class encapsulates the logic for making API calls, handling the conversation
    history using the 'previous_response_id' mechanism, and processing screenshots.
    It uses a single method 'run_step' to handle both the initial task request
    and subsequent steps in the interaction loop.

    Attributes:
        display_width (int): The width of the display/browser window in pixels.
        display_height (int): The height of the display/browser window in pixels.
        url (str | None): Optional URL associated with the agent's context.
        page_name (str | None): Optional page name associated with the agent's context.
        environment (str): The operating environment ('browser', 'mac', 'windows', 'ubuntu').
        client (OpenAI): The OpenAI client instance used for API calls.
        system_prompt (str): Content loaded from the system prompt file.
        rules (str): Content loaded from the rules file.
        context (str): Content loaded from the context file.
        last_response_id (str | None): Stores the ID of the most recent successful API response.
                                       Initialized to None. Used to link conversation steps.
    """

    def __init__(self,
                 display_width: int,
                 display_height: int,
                 context_path: str,
                 system_prompt_path: str,
                 rules_path: str,
                 url: str | None = None,
                 page_name: str | None = None,
                 environment: str = "browser",
                 openai_client: OpenAI | None = None):
        """
        Initializes the ComputerAgent instance.

        Loads configuration, sets up the OpenAI client, and prepares the initial state.

        Args:
            display_width: The width of the display/browser window in pixels.
            display_height: The height of the display/browser window in pixels.
            context_path: Path to the markdown file containing context information.
            system_prompt_path: Path to the markdown file containing the system prompt.
            rules_path: Path to the markdown file containing rules for the agent.
            url: Optional URL of the current page/context.
            page_name: Optional name/title of the current page/context.
            environment: The operating environment ('browser', 'mac', 'windows', 'ubuntu').
                         Defaults to 'browser'.
            openai_client: An optional pre-configured OpenAI client instance.
                           If None, a new client will be created using environment variables
                           (ensure OPENAI_API_KEY is set).

        Raises:
            FileNotFoundError: If any of the provided markdown file paths do not exist.
            IOError: If there is an error reading the markdown files.
            ValueError: If display dimensions are invalid or environment is unsupported.
            AuthenticationError: If the OpenAI client cannot be initialized (e.g., missing key).
            Exception: For other initialization errors.
        """
        print("Initializing ComputerAgent...")
        # --- Input Validation ---
        if not isinstance(display_width, int) or display_width <= 0:
            raise ValueError("display_width must be a positive integer.")
        if not isinstance(display_height, int) or display_height <= 0:
            raise ValueError("display_height must be a positive integer.")
        if environment not in ["browser", "mac", "windows", "ubuntu"]:
            raise ValueError(f"Unsupported environment: {environment}. Must be one of 'browser', 'mac', 'windows', 'ubuntu'.")

        # --- Store Configuration ---
        self.display_width = display_width
        self.display_height = display_height
        self.url = url
        self.page_name = page_name
        self.environment = environment
        print(f"Configuration: {display_width}x{display_height}, Env: {environment}, URL: {url}, Page: {page_name}")

        # --- Initialize OpenAI Client ---
        try:
            # Use provided client or create a new one (requires env var OPENAI_API_KEY)
            self.client = openai_client if openai_client else OpenAI()
            print("OpenAI client initialized successfully.")
            # You might want to add a test ping here if needed, e.g., list models
            # self.client.models.list()
        except AuthenticationError as e:
             print(f"Fatal Error: OpenAI Authentication failed during client initialization: {e}")
             raise # Critical error, cannot proceed
        except Exception as e:
            # Catch other potential errors during client initialization
            print(f"Fatal Error: Failed to initialize OpenAI client: {e}")
            raise # Critical error, cannot proceed

        # --- Load Prompts/Context from Files ---
        # Use a helper method to avoid code repetition and centralize error handling
        try:
            print(f"Loading system prompt from: {system_prompt_path}")
            self.system_prompt = self._read_file_content(system_prompt_path)
            print(f"Loading rules from: {rules_path}")
            self.rules = self._read_file_content(rules_path)
            print(f"Loading context from: {context_path}")
            self.context = self._read_file_content(context_path)
            print("Configuration files loaded successfully.")
        except (FileNotFoundError, IOError) as e:
            # Error is logged inside _read_file_content, re-raise to halt initialization
            raise

        # --- State Management Initialization ---
        self.last_response_id: str | None = None # Stores the ID of the last successful API response
        print("Agent state initialized (last_response_id = None).")
        print("ComputerAgent initialization complete.")

    def _read_file_content(self, file_path: str) -> str:
        """
        Internal helper method to read content from a specified file path.

        Args:
            file_path: The path to the file to read.

        Returns:
            The content of the file as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If an error occurs during file reading.
        """
        if not os.path.exists(file_path):
            print(f"Error: Configuration file not found at path: {file_path}")
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Successfully read {len(content)} characters from {file_path}")
                return content
        except IOError as e:
            print(f"Error: Could not read file {file_path}: {e}")
            raise IOError(f"Error reading file {file_path}: {e}")
        except Exception as e:
             print(f"Error: An unexpected error occurred while reading {file_path}: {e}")
             raise

    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        Internal helper method to read an image file and encode it to a base64 string.

        Args:
            image_path: The path to the image file.

        Returns:
            The base64 encoded string of the image.

        Raises:
            FileNotFoundError: If the image file does not exist.
            IOError: If an error occurs reading the image file.
            ValueError: If an error occurs during base64 encoding.
        """
        if not os.path.exists(image_path):
            print(f"Error: Screenshot file not found at path: {image_path}")
            raise FileNotFoundError(f"Screenshot file not found: {image_path}")
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                print(f"Successfully encoded image {image_path} to base64 ({len(encoded_string)} chars).")
                return encoded_string
        except IOError as e:
            print(f"Error: Could not read screenshot file {image_path}: {e}")
            raise IOError(f"Error reading screenshot file {image_path}: {e}")
        except Exception as e:
             # Catch potential base64 encoding errors or other issues
             print(f"Error: Failed to encode image file {image_path} to base64: {e}")
             raise ValueError(f"Error encoding image file {image_path} to base64: {e}")

    def run_step_with_memory(self,
                 task_or_previous_call_id: str,
                 screenshot_path: str,
                 acknowledged_safety_checks: list | None = None):
        """
        (Original run_step method renamed)
        Executes a single step in the computer interaction loop via the OpenAI API.

        This method intelligently handles both the initial call (when the agent's
        'last_response_id' is None) and subsequent calls in the conversation loop
        by using the 'previous_response_id' parameter when appropriate.

        TODO: Fix call_id handling for subsequent calls. The caller (e.g., adsetAgentController)
              needs to extract the 'call_id' from the 'computer_call' action in the response
              and pass it correctly as 'task_or_previous_call_id' for the *next* step when
              using this memory-based approach. The current implementation likely fails because
              the full response string or task description is passed instead of the specific call_id.

        Args:
            task_or_previous_call_id (str):
                - For the *initial* call: This should be the user's task description (e.g., "Book a flight to London").
                - For *subsequent* calls: This must be the 'call_id' (string) obtained from the
                  'computer_call' action object within the previous API response.
            screenshot_path (str): The file path to the PNG screenshot representing the current
                                   state of the environment after the last action (or the initial state).
            acknowledged_safety_checks (list | None): An optional list of safety check objects that
                                        the user has explicitly acknowledged. This is required if the
                                        previous API response included 'pending_safety_checks'.
                                        Defaults to None.

        Returns:
            The complete response object from the OpenAI API upon successful execution.

        Raises:
            FileNotFoundError: If the screenshot file path does not exist.
            IOError: If there is an error reading the screenshot file.
            ValueError: If there is an error encoding the screenshot, or if input args are invalid for the call type.
            openai.AuthenticationError: If authentication with OpenAI fails.
            openai.RateLimitError: If the OpenAI API rate limit is exceeded.
            openai.BadRequestError: If the request structure is invalid (check inputs and state).
            openai.APIError: For other general OpenAI API related errors.
            Exception: For any other unexpected errors during the process.
        """
        print(f"\n--- Running Agent Step (WITH MEMORY) ---")
        print(f"Current last_response_id: {self.last_response_id}")
        print(f"Received task/call_id: '{task_or_previous_call_id}'")
        print(f"Using screenshot: {screenshot_path}")
        if acknowledged_safety_checks:
             print(f"Acknowledged safety checks provided: {acknowledged_safety_checks}")

        # --- 1. Prepare Screenshot ---
        try:
            screenshot_base64 = self._encode_image_to_base64(screenshot_path)
            # Format the image data as a data URI for the API
            image_url = f"data:image/png;base64,{screenshot_base64}"
        except (FileNotFoundError, IOError, ValueError) as e:
            # Error logged in helper, re-raise to stop execution
            raise

        # --- 2. Prepare Common API Request Parameters ---
        # These parameters are common to both initial and subsequent calls
        request_params = {
            "model": "computer-use-preview",
            "tools": [{
                "type": "computer_use_preview",
                "display_width": self.display_width,
                "display_height": self.display_height,
                "environment": self.environment
                # Add 'generate_summary': 'concise'/'detailed' here if you want reasoning items
                # "reasoning": { "generate_summary": "concise" }
            }],
            "truncation": "auto", # Required for computer_use_preview tool
            "input": [] # Input list will be populated based on call type
        }

        # --- 3. Determine Call Type and Construct Specific Inputs ---
        if self.last_response_id is None:
            # ---=== INITIAL CALL LOGIC ===---
            print("Call Type: Initial (Memory Mode)")
            # In the first call, the first argument is interpreted as the task description
            task_description = task_or_previous_call_id
            if not isinstance(task_description, str) or not task_description.strip():
                 print("Error: Initial call requires a non-empty task description.")
                 raise ValueError("Task description (string) is required for the initial call.")

            # Construct the detailed initial prompt using XML-like tags for clarity
            content_parts = []
            if self.system_prompt:
                content_parts.append(f"<system_prompt>\n{self.system_prompt}\n</system_prompt>")
            if self.rules:
                content_parts.append(f"<rules>\n{self.rules}\n</rules>")
            if self.context:
                content_parts.append(f"<context>\n{self.context}\n</context>")
            # Add optional URL and Page Name if they exist
            if self.url:
                content_parts.append(f"<url>{self.url}</url>")
            if self.page_name:
                 content_parts.append(f"<page_name>{self.page_name}</page_name>")
            # Add the specific task for this run
            content_parts.append(f"<task>\n{task_description}\n</task>")

            # Join parts with double newline for separation
            full_content_string = "\n\n".join(content_parts)
            print(f"Constructed Initial Prompt Content (excluding file content details):\n"
                  f"<system_prompt>...</system_prompt>\n\n"
                  f"<rules>...</rules>\n\n"
                  f"<context>...</context>\n\n"
                  f"{'<url>'+self.url+'</url>\n\n' if self.url else ''}"
                  f"{'<page_name>'+self.page_name+'</page_name>\n\n' if self.page_name else ''}"
                  f"<task>...</task>") # Avoid printing potentially large prompts

            # Build the input list for the first call: User prompt + Initial screenshot
            # Format matches the successful example in computer_agent_request.py
            request_params["input"].append({
                "role": "user",
                "content": [
                    {"type": "input_text", "text": full_content_string},
                    {"type": "input_image", "image_url": image_url}
                ]
            })
            
            # Add reasoning configuration
            request_params["reasoning"] = {
                "generate_summary": "concise"
            }

        else:
            # ---=== SUBSEQUENT CALL LOGIC ===---
            print("Call Type: Subsequent (Memory Mode)")
            # In subsequent calls, the first argument is interpreted as the previous call_id
            previous_call_id = task_or_previous_call_id
            if not isinstance(previous_call_id, str) or not previous_call_id.startswith("call_"):
                 print(f"Error: Subsequent call requires a valid 'call_id' (string starting with 'call_'), got: {previous_call_id}")
                 raise ValueError("Subsequent calls require the 'call_id' from the previous computer_call action.")

            # Construct the computer_call_output object, which primarily contains the new screenshot
            computer_output = {
                "type": "computer_call_output",
                "call_id": previous_call_id, # Links this output to the previous action request
                "output": {
                    "type": "input_image", # The result of the action is the new visual state
                    "image_url": image_url
                    # Optionally add current_url here if it changed and you want better safety checks
                    # "current_url": "https://new-url.com/page"
                }
            }
            # Include acknowledged safety checks if they were provided
            if acknowledged_safety_checks:
                 # Validate format if needed (should be a list of dicts with 'id', 'code', 'message')
                if isinstance(acknowledged_safety_checks, list):
                    computer_output["acknowledged_safety_checks"] = acknowledged_safety_checks
                    print(f"Including acknowledged safety checks in the request.")
                else:
                    print("Warning: acknowledged_safety_checks provided but is not a list. Ignoring.")

            # The input list for subsequent calls contains *only* the computer_call_output
            request_params["input"].append(computer_output)

            # Crucially, add the previous_response_id to link the history
            request_params["previous_response_id"] = self.last_response_id
            print(f"Using previous_response_id: {self.last_response_id}")


        # --- 4. Execute API Call ---
        # Use ** to unpack the prepared dictionary into keyword arguments
        print("Sending request to OpenAI API...")
        # For debugging, print params excluding potentially huge image data
        # print(f"API Request Params (excluding input details): { {k:v for k,v in request_params.items() if k != 'input'} }")

        try:
            # Make the actual API call
            response = self.client.responses.create(**request_params)
            # If the call returns successfully:
            print("API call successful.")

            # --- 5. Update Agent State ---
            # Store the ID from the *new* response, to be used in the *next* step
            self.last_response_id = response.id
            print(f"Successfully updated last_response_id to: {self.last_response_id}")

            # Return the full response object for the caller to process
            return response

        # --- 6. Handle Specific API Errors ---
        except AuthenticationError as e:
            # Usually due to invalid API key
            print(f"Fatal Error: OpenAI Authentication Error: {e}. Please check your API key configuration.")
            # Authentication errors are critical, re-raise
            raise
        except RateLimitError as e:
            # API limit hit, often requires waiting or upgrading plan
            print(f"Error: OpenAI Rate Limit Exceeded: {e}. Consider adding delays or checking your usage limits.")
            # Re-raise so the caller can potentially implement retry logic with backoff
            raise
        except BadRequestError as e:
             # Often indicates a problem with the request structure (e.g., invalid input format,
             # missing required fields, issue with previous_response_id linkage)
             print(f"Error: OpenAI Bad Request Error (4xx): {e}. This often indicates an issue with the request data or structure.")
             print(f"Status Code: {e.status_code}")
             # Consider trying to parse the response body for more details if available
             # print(f"Response Body: {e.response.text if e.response else 'N/A'}") # Example
             # Depending on the error, the state (last_response_id) might be invalid.
             # Resetting might be appropriate in some cases, but can be complex.
             # For now, re-raise to indicate the step failed.
             # self.last_response_id = None # Cautious reset? Maybe not ideal.
             raise
        except APIError as e:
            # Catch other generic API errors (e.g., 5xx server errors)
            print(f"Error: OpenAI API Error: {e}. Status Code: {e.status_code}")
            # These might be transient, re-raising allows for potential retries by caller
            raise
        # --- 7. Handle Other Unexpected Errors ---
        except Exception as e:
            # Catch anything else that might have gone wrong
            print(f"Fatal Error: An unexpected error occurred during the API call execution: {e}")
            # Consider logging the full traceback here
            # import traceback
            # traceback.print_exc()
            # It's hard to know the state validity here, re-raise
            raise

    def run_step(self,
                 task: str,
                 screenshot_path: str):
        """
        Executes a single, stateless step via the OpenAI Computer Use API.

        This method treats every call as independent, sending the full context
        (system prompt, rules, context, url, page name, task) along with the
        screenshot. It does NOT use 'previous_response_id' or expect 'call_id'.

        Args:
            task (str): The specific task description for this independent analysis
                        (e.g., "Click the 'Login' button", "Verify settings saved").
            screenshot_path (str): The file path to the PNG screenshot representing
                                   the current state of the environment.

        Returns:
            The complete response object from the OpenAI API upon successful execution.

        Raises:
            FileNotFoundError: If the screenshot file path does not exist.
            IOError: If there is an error reading the screenshot file.
            ValueError: If there is an error encoding the screenshot or task is empty.
            openai.AuthenticationError: If authentication with OpenAI fails.
            openai.RateLimitError: If the OpenAI API rate limit is exceeded.
            openai.BadRequestError: If the request structure is invalid.
            openai.APIError: For other general OpenAI API related errors.
            Exception: For any other unexpected errors during the process.
        """
        print(f"\n--- Running Agent Step (STATELESS) ---")
        print(f"Received task: '{task}'")
        print(f"Using screenshot: {screenshot_path}")

        # --- 1. Prepare Screenshot ---
        try:
            screenshot_base64 = self._encode_image_to_base64(screenshot_path)
            image_url = f"data:image/png;base64,{screenshot_base64}"
        except (FileNotFoundError, IOError, ValueError) as e:
            raise

        # --- 2. Prepare API Request Parameters (Always Initial Structure) ---
        request_params = {
            "model": "computer-use-preview",
            "tools": [{
                "type": "computer_use_preview",
                "display_width": self.display_width,
                "display_height": self.display_height,
                "environment": self.environment
            }],
            "truncation": "auto",
            "input": [],
            "reasoning": {"generate_summary": "concise"}
        }

        # --- 3. Construct Input (Always Initial Format) ---
        print("Call Type: Stateless (Always treated as Initial)")
        if not isinstance(task, str) or not task.strip():
             print("Error: Stateless call requires a non-empty task description.")
             raise ValueError("Task description (string) is required for the stateless call.")

        content_parts = []
        if self.system_prompt: content_parts.append(f"<system_prompt>\n{self.system_prompt}\n</system_prompt>")
        if self.rules: content_parts.append(f"<rules>\n{self.rules}\n</rules>")
        if self.context: content_parts.append(f"<context>\n{self.context}\n</context>")
        if self.url: content_parts.append(f"<url>{self.url}</url>")
        if self.page_name: content_parts.append(f"<page_name>{self.page_name}</page_name>")
        content_parts.append(f"<task>\n{task}\n</task>") # Use the provided task
        full_content_string = "\n\n".join(content_parts)
        print(f"Constructed Stateless Prompt Content (structure only)")

        request_params["input"].append({
            "role": "user",
            "content": [
                {"type": "input_text", "text": full_content_string},
                {"type": "input_image", "image_url": image_url}
            ]
        })

        # --- 4. Execute API Call ---
        print("Sending request to OpenAI API (Stateless Mode)...")
        try:
            response = self.client.responses.create(**request_params)
            print("API call successful (Stateless Mode).")

            # --- 5. NO State Update ---
            # self.last_response_id is NOT updated in stateless mode

            return response

        # --- 6/7. Handle Errors (Identical error handling logic) ---
        except AuthenticationError as e:
            print(f"Fatal Error: OpenAI Authentication Error: {e}.")
            raise
        except RateLimitError as e:
            print(f"Error: OpenAI Rate Limit Exceeded: {e}.")
            raise
        except BadRequestError as e:
             print(f"Error: OpenAI Bad Request Error (4xx): {e}.")
             print(f"Status Code: {e.status_code}")
             raise
        except APIError as e:
            print(f"Error: OpenAI API Error: {e}. Status Code: {e.status_code}")
            raise
        except Exception as e:
            print(f"Fatal Error: An unexpected error occurred during the API call execution: {e}")
            raise

# --- Example Usage (Illustrative) ---
if __name__ == "__main__":
    # This block will only run when the script is executed directly
    # Replace with your actual file paths and details

    # Create dummy files for testing
    try:
        os.makedirs("agent_config", exist_ok=True)
        with open("agent_config/system.md", "w") as f: f.write("You are a helpful assistant using a computer.")
        with open("agent_config/rules.md", "w") as f: f.write("1. Be precise.\n2. Click carefully.")
        with open("agent_config/context.md", "w") as f: f.write("The user wants to find the cheapest flight.")
        # Use a real screenshot from the specified path
        REAL_SCREENSHOT_PATH = "/Users/meirsabag/Public/browser_use_ver4_newVersion/training_images/output_images_condition_stop_audience_page/screenshot_2025-03-27_13-05-52_396.png"
        if os.path.exists(REAL_SCREENSHOT_PATH):
            print(f"Using real screenshot from: {REAL_SCREENSHOT_PATH}")
            # Copy the real image to our working files
            import shutil
            shutil.copy(REAL_SCREENSHOT_PATH, "initial_screenshot.png")
            shutil.copy(REAL_SCREENSHOT_PATH, "action_screenshot.png")
            print("Real screenshot copied for example use.")
        else:
            print(f"Error: Real screenshot not found at {REAL_SCREENSHOT_PATH}")
            print("Falling back to creating empty placeholder files.")
            open("initial_screenshot.png", 'a').close()
            open("action_screenshot.png", 'a').close()


        # --- Configuration ---
        DISPLAY_WIDTH = 1024
        DISPLAY_HEIGHT = 768
        CONTEXT_PATH = "agent_config/context.md"
        SYSTEM_PROMPT_PATH = "agent_config/system.md"
        RULES_PATH = "agent_config/rules.md"
        SCREENSHOT_PATH_1 = "initial_screenshot.png"
        SCREENSHOT_PATH_2 = "action_screenshot.png"
        INITIAL_TASK = "Find the cheapest flight from TLV to LHR on skyscanner.com"

        # --- Initialization ---
        # Make sure OPENAI_API_KEY environment variable is set
        try:
            agent = ComputerAgent(
                display_width=DISPLAY_WIDTH,
                display_height=DISPLAY_HEIGHT,
                context_path=CONTEXT_PATH,
                system_prompt_path=SYSTEM_PROMPT_PATH,
                rules_path=RULES_PATH,
                # url="https://www.skyscanner.com" # Optional
            )

            # --- First Step ---
            print("\n=== Running First Step ===")
            response1 = agent.run_step(
                task_or_previous_call_id=INITIAL_TASK,
                screenshot_path=SCREENSHOT_PATH_1
            )

            print("\n--- Response 1 Received ---")
            # Process response1 - check for computer_call actions
            # (This part requires parsing the response object)
            first_action = None
            if response1 and response1.output:
                 print("Response 1 Output:")
                 for item in response1.output:
                     print(f"- Type: {item.type}")
                     if item.type == 'computer_call':
                         first_action = item # Get the action details
                         print(f"  Action: {item.action.type}, Call ID: {item.call_id}")
                         # You would execute this action (e.g., click, type) here
                         # using Playwright, Selenium, OS automation libs etc.
                     elif item.type == 'reasoning':
                         print(f"  Reasoning: {item.summary}")
                     elif item.type == 'text':
                         print(f"  Text: {item.text}")

            # --- Simulate Action Execution & Get Next Screenshot ---
            # In a real scenario, you'd execute first_action.action here
            # and take a new screenshot (SCREENSHOT_PATH_2)

            # --- Second Step (if an action was suggested) ---
            if first_action:
                 print("\n=== Running Second Step ===")
                 # Assume first_action.action was executed and SCREENSHOT_PATH_2 is ready
                 response2 = agent.run_step(
                     task_or_previous_call_id=first_action.call_id, # Use call_id from previous step
                     screenshot_path=SCREENSHOT_PATH_2
                     # Add acknowledged_safety_checks=... if response1 had pending checks
                 )
                 print("\n--- Response 2 Received ---")
                 # Process response2 similarly...
                 if response2 and response2.output:
                      print("Response 2 Output:")
                      for item in response2.output:
                           print(f"- Type: {item.type}")
                           # ... further processing ...
            else:
                 print("\nNo computer action suggested in the first response.")


        except (FileNotFoundError, IOError, ValueError, APIError, Exception) as e:
             print(f"\n--- An error occurred during the example execution ---")
             print(e)
             # Add more specific error handling or logging as needed

    finally:
         # Clean up dummy files
         # try:
         #      os.remove("agent_config/system.md")
         #      os.remove("agent_config/rules.md")
         #      os.remove("agent_config/context.md")
         #      os.rmdir("agent_config")
         #      os.remove("initial_screenshot.png")
         #      os.remove("action_screenshot.png")
         #      print("\nCleaned up dummy files.")
         # except OSError as e:
         #      print(f"\nWarning: Could not clean up all dummy files: {e}")
         pass # Comment out cleanup for inspection if needed