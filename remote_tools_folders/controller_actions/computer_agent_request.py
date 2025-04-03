import os
import base64
import logging
import json
from datetime import datetime
from openai import OpenAI, APIError # Import APIError for specific error handling
from dotenv import load_dotenv

# --- Configuration ---

# Load environment variables from .env file
load_dotenv()

# Configure logging for detailed terminal output
# This sets up logging to show timestamp, log level, and message
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Define the directory where images are stored
IMAGE_DIRECTORY = "images"
# Define the directory where response logs will be saved
LOG_DIRECTORY = "response_logs"

# --- Helper Functions ---

def encode_image_to_base64(image_path):
    """
    Reads an image file, encodes it to Base64, and returns the Base64 string.

    Args:
        image_path (str): The full path to the image file.

    Returns:
        str: The Base64 encoded string of the image, or None if an error occurs.
    """
    logging.debug(f"Attempting to encode image: {image_path}")
    try:
        # Open the image file in binary read mode ('rb')
        with open(image_path, "rb") as image_file:
            # Read the binary content of the image
            image_content = image_file.read()
            # Encode the binary content to Base64
            base64_bytes = base64.b64encode(image_content)
            # Decode the Base64 bytes into a UTF-8 string
            base64_string = base64_bytes.decode('utf-8')
            logging.info(f"Successfully encoded image: {image_path}")
            return base64_string
    except FileNotFoundError:
        logging.error(f"Error: Image file not found at {image_path}")
        return None
    except Exception as e:
        logging.error(f"Error encoding image {image_path}: {e}")
        return None

def format_image_for_api(base64_string, image_type="png"):
    """
    Formats the Base64 encoded image string into the required data URI format for the API.

    Args:
        base64_string (str): The Base64 encoded image string.
        image_type (str): The image format (e.g., 'png', 'jpeg'). Defaults to 'png'.

    Returns:
        str: The formatted data URI string (e.g., "data:image/png;base64,...").
    """
    # **IMPORTANT**: This is the required format for image URLs in the API request.
    # It must start with "data:image/[image_type];base64," followed by the encoded string.
    data_uri = f"data:image/{image_type};base64,{base64_string}"
    logging.debug(f"Formatted image data URI (first 50 chars): {data_uri[:50]}...")
    return data_uri

def log_response_to_file(response_data, filename_prefix="response"):
    """
    Logs the full API response data to a JSON file with a timestamp.

    Args:
        response_data (object): The response object from the OpenAI API call.
        filename_prefix (str): The prefix for the log file name.
    """
    # Create the log directory if it doesn't exist
    os.makedirs(LOG_DIRECTORY, exist_ok=True)

    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{filename_prefix}_{timestamp}.json"
    log_file_path = os.path.join(LOG_DIRECTORY, log_filename)

    logging.info(f"Attempting to log response to: {log_file_path}")
    try:
        # Use the model_dump_json method for Pydantic models (like the OpenAI response)
        # It serializes the object to a JSON string, handling complex types.
        # 'indent=2' makes the JSON file human-readable.
        json_output = response_data.model_dump_json(indent=2)

        # Write the JSON string to the log file
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write(json_output)
        logging.info(f"Successfully logged response to {log_file_path}")
    except AttributeError:
        # Fallback if the response object doesn't have model_dump_json (shouldn't happen with OpenAI client)
        logging.warning("Response object doesn't have 'model_dump_json'. Trying standard json dump.")
        try:
            with open(log_file_path, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)
            logging.info(f"Successfully logged response (using standard json) to {log_file_path}")
        except Exception as e:
             logging.error(f"Failed to log response using standard json: {e}")
    except Exception as e:
        logging.error(f"Failed to write response log to {log_file_path}: {e}")


def send_initial_computer_request(prompt_text, image_filename):
    """
    Sends the initial request to the OpenAI Computer Use API with a prompt and an image.

    Args:
        prompt_text (str): The user's instruction or goal.
        image_filename (str): Either the full path to the image file or just the filename in IMAGE_DIRECTORY.

    Returns:
        object: The OpenAI API response object, or None if an error occurred.
    """
    logging.info("--- Starting Initial Computer Use Request ---")

    # --- 1. Initialize OpenAI Client ---
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.critical("Error: OPENAI_API_KEY environment variable not set.")
        return None
    logging.debug("OpenAI API Key loaded from environment variable.")

    try:
        # Create the OpenAI client instance
        client = OpenAI(api_key=api_key)
        logging.debug("OpenAI client initialized.")
    except Exception as e:
        logging.critical(f"Failed to initialize OpenAI client: {e}")
        return None

    # --- 2. Prepare Image ---
    # Check if image_filename is already a full path
    if os.path.isabs(image_filename):
        full_image_path = image_filename
    else:
        # Construct the full path to the image from relative path
        full_image_path = os.path.join(IMAGE_DIRECTORY, image_filename)
    logging.debug(f"Full image path: {full_image_path}")

    # Encode the image to Base64
    base64_image = encode_image_to_base64(full_image_path)
    if not base64_image:
        # Error already logged in encode_image_to_base64
        return None

    # Format the Base64 string as a data URI for the API
    image_url_for_api = format_image_for_api(base64_image)

    # ----------->>>> 3. Construct API Request Payload <<<<<-----------
    # Define the model and tools configuration
    # Using 'computer-use-preview' model as specified
    model_name = "computer-use-preview"
    # Define the tool with necessary parameters (display size, environment)
    # Adjust display_width, display_height, and environment as needed for your setup
    tools_config = [
        {
            "type": "computer_use_preview",
            "display_width": 1024,  # Example width
            "display_height": 768,  # Example height
            "environment": "browser" # Example environment: "browser", "mac", "windows", "ubuntu"
        }
    ]
    # Define the input messages, including the user prompt and the initial screenshot
    input_payload = [
        {
            "role": "user",
            "content": [
                { "type": "input_text", "text": prompt_text },
                {
                    "type": "input_image",
                    "image_url": image_url_for_api # Use the formatted data URI
                }
            ]
        }
    ]
    # Request reasoning summary (optional, can be "concise", "detailed", or None)
    reasoning_config = {
        "generate_summary": "concise",
    }
    # **IMPORTANT**: Truncation must be set to "auto" for computer_use_preview tool
    truncation_setting = "auto"

    logging.debug(f"API Request Details:")
    logging.debug(f"  Model: {model_name}")
    logging.debug(f"  Tools Config: {tools_config}")
    logging.debug(f"  Input Payload (Prompt): {prompt_text}")
    logging.debug(f"  Input Payload (Image): Sent (data URI)")
    logging.debug(f"  Reasoning Config: {reasoning_config}")
    logging.debug(f"  Truncation: {truncation_setting}")

    # --- 4. Send Request to OpenAI API ---
    try:
        logging.info("Sending request to OpenAI Responses API...")
        response = client.responses.create(
            model=model_name,
            tools=tools_config,
            input=input_payload,
            reasoning=reasoning_config,
            truncation=truncation_setting
        )
        logging.info("Received response from OpenAI API.")
        logging.debug(f"Response ID: {response.id}")
        # The full response object will be logged to the file later
        return response

    except APIError as e:
        # Handle specific API errors (e.g., authentication, rate limits)
        logging.error(f"OpenAI API Error: {e.status_code} - {e.message}")
        logging.error(f"Full API Error details: {e}")
        return None
    except Exception as e:
        # Handle other potential errors (e.g., network issues)
        logging.error(f"An unexpected error occurred during API call: {e}")
        return None

# --- Main Execution ---
if __name__ == "__main__":
    logging.info("Script started.")

    # --- Define Inputs ---
    # The user's goal or instruction
    user_prompt = """
    Click on the text \"Custom audiences\" (where it currently says \"None\" below it). This should expand the section and reveal the search box or creation options.
    Please note that if this is not an edit screen of the campaign, then you should write none.
    
    """
    # The name of the image file in the 'images' directory
    image_path = '/Users/meirsabag/Public/browser_use_ver4_newVersion/training_images/output_images_condition_stop_audience_page/1.png'

    # --- Execute Request ---
    api_response = send_initial_computer_request(user_prompt, image_path)

    # --- Process Response ---
    if api_response:
        logging.info("API request successful.")
        # Log the entire response object to a timestamped JSON file
        log_response_to_file(api_response, filename_prefix="initial_request_response")

        # Print raw response to console
        print("\n--- Raw API Response ---")
        print(api_response.model_dump_json(indent=2))
        print("--- End of Raw API Response ---\n")

        # You can optionally extract and print specific parts of the response here
        # For example, checking for 'computer_call' items:
        suggested_actions = []
        reasoning_summary = []
        if hasattr(api_response, 'output') and api_response.output:
             for item in api_response.output:
                if item.type == "computer_call":
                    logging.info(f"Received suggested action: {item.action.type}")
                    suggested_actions.append(item)
                elif item.type == "reasoning" and hasattr(item, 'summary'):
                     summary_texts = [s.text for s in item.summary if s.type == 'summary_text']
                     logging.info(f"Received reasoning summary: {' '.join(summary_texts)}")
                     reasoning_summary.append(item)
                else:
                    logging.debug(f"Received other output item type: {item.type}")
        else:
             logging.warning("Response object did not contain an 'output' attribute or it was empty.")

        if not suggested_actions:
             logging.info("The model did not return a 'computer_call' action in this response.")

    else:
        logging.error("API request failed. Check logs above for details.")

    logging.info("Script finished.")