"""
Facebook Ads Manager Assistant with Gemini AI

This script uses Google's Gemini AI model to analyze screenshots of Facebook Ads Manager 
and provide step-by-step guidance for configuring a lookalike audience. 

The program works by:
1. Loading example screenshots from specified paths
2. Sending these images to the Gemini model along with example conversations
3. Providing instructions through a system prompt stored in a separate file
4. Streaming the model's response to the console

Requirements:
- Google Gemini API key (set as GEMINI_API_KEY environment variable)
- The google-genai Python package
- Example images at the specified paths
- Markdown files containing example responses
"""

import base64
import os
import sys
import datetime
from google import genai  # Google's Generative AI Python client
from google.generativeai import types  # Type definitions for the Gemini API
import traceback # Add traceback for error logging
import logging # Import the logging module

# Import utilities for logging
from utils import log_request, log_response


def read_markdown_file(file_path):
    """
    Reads content from a markdown file.
    
    Args:
        file_path (str): Path to the markdown file to read
        
    Returns:
        str: The content of the markdown file
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def generate(user_image_path=None, user_text="INSERT_INPUT_HERE"):
    """
    Main function that:
    1. Sets up the Gemini API client
    2. Uploads example images and user image if provided
    3. Loads example responses and system prompt from files
    4. Configures and sends the request to the Gemini model
    5. Streams the response back to the console
    
    Args:
        user_image_path (str, optional): Path to a user-provided image to analyze
        user_text (str, optional): Text input from the user
    Returns:
        str: The full response text from the Gemini model. Returns None if an error occurs.
    """
    full_response = "" # Initialize variable to store the full response
    try: # Add try block for error handling
        # Initialize the Gemini client with API key from environment variable
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )

        # Upload the three example screenshots to the Gemini API
        # These screenshots show different stages of the Facebook Ads Manager workflow
        files = [
            # Screenshot 1: Campaign level page
            client.files.upload(file="adset_training_images/1.png"),
            # Screenshot 2: Ad set level page (top part visible)
            client.files.upload(file="adset_training_images/2.png"),
            # Screenshot 3: Ad set level page (audience section visible)
            client.files.upload(file="adset_training_images/6.png"),
        ]
        
        # Read example model responses from Markdown files
        # These contain pre-written text showing how the model should respond to each scenario
        response1 = read_markdown_file("model_response_few_shots/response1.md")  # Response for screenshot 1
        response1_reasoning = read_markdown_file("model_response_few_shots/response1_reasoning.md")  # Reasoning for screenshot 1
        response2 = read_markdown_file("model_response_few_shots/response2.md")  # Response for screenshot 2
        response2_reasoning = read_markdown_file("model_response_few_shots/response2_reasoning.md")  # Reasoning for screenshot 2
        response3 = read_markdown_file("model_response_few_shots/response3.md")  # Response for screenshot 3
        response3_reasoning = read_markdown_file("model_response_few_shots/response3_reasoning.md")  # Reasoning for screenshot 3
        
        # Read the system prompt that guides the model's behavior
        system_prompt = read_markdown_file("system_prompt.md")
        
        # Specify which Gemini model to use
        model = "gemini-2.5-pro-exp-03-25"
        
        # Prepare the final user query based on provided parameters
        final_user_parts = []
        
        # If an image path is provided, upload and include it
        if user_image_path and os.path.exists(user_image_path):
            user_image = client.files.upload(file=user_image_path)
            final_user_parts.append(
                types.Part.from_uri(
                    file_uri=user_image.uri,
                    mime_type=user_image.mime_type,
                )
            )
        else:
             # Handle case where image path is missing or invalid if necessary
             logging.warning(f"User image path not provided or invalid: {user_image_path}")
             # Decide if you want to proceed without an image or return an error
        
        # Add the text input
        if user_text:
            final_user_parts.append(types.Part.from_text(text=user_text))
        
        # Build the conversation history to provide context for the model
        # This demonstrates a few examples of how the model should respond to different scenarios
        contents = [
            # First example: User submits screenshot 1 with task description
            types.Content(
                role="user",
                parts=[
                    # The screenshot showing the campaign level page
                    types.Part.from_uri(
                        file_uri=files[0].uri,
                        mime_type=files[0].mime_type,
                    ),
                    # The user's task description
                    types.Part.from_text(text="""The task is to run the campaign with a lookalike audience."""),
                ],
            ),
            # Model response to the first example
            types.Content(
                role="model",
                parts=[
                    types.Part.from_text(text=response1),  # Main response explaining what to do
                    types.Part.from_text(text=response1_reasoning),  # Detailed reasoning and explanation
                ],
            ),
            
            # Second example: User submits screenshot 2 with task description
            types.Content(
                role="user",
                parts=[
                    # The screenshot showing the ad set page (top sections)
                    types.Part.from_uri(
                        file_uri=files[1].uri,
                        mime_type=files[1].mime_type,
                    ),
                    # The user's task description (same as before)
                    types.Part.from_text(text="""The task is to run the campaign with a lookalike audience."""),
                ],
            ),
            # Model response to the second example
            types.Content(
                role="model",
                parts=[
                    types.Part.from_text(text=response2),  # Main response explaining what to do
                    types.Part.from_text(text=response2_reasoning),  # Detailed reasoning and explanation
                ],
            ),
            
            # Third example: User submits screenshot 3 (no additional text)
            types.Content(
                role="user",
                parts=[
                    # The screenshot showing the ad set page (audience section)
                    types.Part.from_uri(
                        file_uri=files[2].uri,
                        mime_type=files[2].mime_type,
                    ),
                    # No additional text - the model understands from context
                ],
            ),
            # Model response to the third example
            types.Content(
                role="model",
                parts=[
                    types.Part.from_text(text=response3),  # Main response explaining what to do
                    types.Part.from_text(text=response3_reasoning),  # Detailed reasoning and explanation
                ],
            ),
            
            # Final user query - now dynamically populated with user's input
            types.Content(
                role="user",
                parts=final_user_parts
            ),
        ]
        
        # Configure the generation parameters
        generate_content_config = types.GenerateContentConfig(
            temperature=0.4,  # Lower temperature for more consistent outputs
            response_mime_type="text/plain",  # Return plain text
            system_instruction=[
                types.Part.from_text(text=system_prompt),  # The instructions that guide the model's behavior
            ],
        )
        
        # Create a serializable version of the request for logging
        request_log = {
            "timestamp": datetime.datetime.now().isoformat(),
            "model": model,
            "temperature": generate_content_config.temperature,
            "conversation": [
                {
                    "role": content.role,
                    "parts": [
                        {"type": "text", "content": part.text} if hasattr(part, "text") 
                        else {"type": "file", "uri": part.uri if hasattr(part, "uri") else "image_data"}
                        for part in content.parts
                    ]
                }
                for content in contents
            ],
            "system_instruction": system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt
        }
        
        # Log the request before sending
        log_request(request_log)
        
        # Send the request to the Gemini model and stream the response
        # Streaming allows responses to appear incrementally rather than waiting for the full response

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            # Append each chunk to the full response
            full_response += chunk.text
            # Print each chunk as it arrives (optional, keep or remove based on need)
            # print(chunk.text, end="") # Commented out to avoid duplicate printing if called by another script
        # print() # Add a newline after streaming is complete

        # Log the complete response after all chunks are received
        log_response(full_response)

        return full_response # Return the accumulated response string

    except Exception as e:
        # Log the error
        timestamp = datetime.datetime.now().isoformat()
        error_message = f"[{timestamp}] Error in generate function: {e}\n{traceback.format_exc()}"
        print(error_message, file=sys.stderr) # Print error to stderr
        # Optionally log to a file as well if you have an error logging function
        # log_error(error_message) # Assumes an error logging function exists

        return None # Return None to indicate an error occurred


# If run directly, check for command line arguments
if __name__ == "__main__":
    response = None # Initialize response variable
    if len(sys.argv) > 2:
        # If both image path and text are provided
        response = generate(user_image_path=sys.argv[1], user_text=sys.argv[2])
    elif len(sys.argv) > 1:
        # If only image path is provided, use default text
        response = generate(user_image_path=sys.argv[1])
    else:
        # Use default placeholder
        response = generate()

    # Print the response if the script is run directly
    if response:
        print("\n--- LLM Response ---")
        print(response)
    else:
        print("\n--- LLM call failed ---", file=sys.stderr) 