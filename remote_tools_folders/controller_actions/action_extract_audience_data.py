from browser_use import ActionResult
from browser_use.browser.context import BrowserContext
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import json
import anthropic
import logging
import datetime
import traceback
from dotenv import load_dotenv
import re
import base64

class ExtractAudienceDataAction(BaseModel):
    is_first_run: bool = Field(True, description="Whether this is the first run (create new file) or not (append to existing)")
    file_path: Optional[str] = Field(None, description="Path to the existing JSON file (only used if is_first_run=False)")

async def perform_extract_audience_data(params: ExtractAudienceDataAction, browser: BrowserContext) -> ActionResult:
    """
    Helper function to extract audience data using Claude Vision API.
    """
    logger = None
    file_handler = None
    try:
        # --- Logger Setup ---
        log_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "audience_data_extraction.log")
        logger = logging.getLogger("audience_extraction")
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        if logger.handlers:
            for handler in list(logger.handlers): 
                logger.removeHandler(handler)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S.%f')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        # --- End Logger Setup ---

        session_start_time = datetime.datetime.now()
        logger.info("="*80)
        logger.info(f"STARTING NEW EXTRACTION SESSION: {session_start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        logger.info("="*80)
        logger.info(f"Function parameters: is_first_run={params.is_first_run}, file_path={params.file_path}")

        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded")

        # Default directory for storing extracted data
        agent_files_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/agent-files"
        logger.info(f"Using agent files directory: {agent_files_dir}")

        # Initialize the file path
        file_path = params.file_path

        # If this is the first run, create a new file
        if params.is_first_run:
            # Create the directory if it doesn't exist
            os.makedirs(agent_files_dir, exist_ok=True)
            # Generate a timestamp-based filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(agent_files_dir, f"facebook_audience_data_{timestamp}.json")
            logger.info(f"Generated new file path for first run: {file_path}")
        elif not file_path:
            # If not first run but no file path provided, return an error
            logger.error("No file path provided for subsequent run (not first run)")
            return ActionResult(error="File path must be provided when is_first_run is False")
        else:
            logger.info(f"Using provided file path for subsequent run: {file_path}")

        # Initialize Anthropic client using API key from environment variables
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
            return ActionResult(error="ANTHROPIC_API_KEY not found in environment variables")

        logger.info("Anthropic API key found in environment variables")
        client = anthropic.Anthropic(api_key=api_key)
        logger.info("Anthropic client initialized")

        # Take a screenshot of the current page
        logger.info("Taking screenshot of current page")
        start_time = datetime.datetime.now()
        screenshot_data = await browser.take_screenshot(full_page=True)
        end_time = datetime.datetime.now()
        screenshot_duration = (end_time - start_time).total_seconds()

        if not screenshot_data:
            logger.error("Failed to capture screenshot")
            return ActionResult(error="Failed to capture screenshot")

        screenshot_size = len(screenshot_data)
        logger.info(f"Screenshot captured successfully: {screenshot_size} characters, took {screenshot_duration:.2f} seconds")

        # Detect image format from base64 prefix or assume png/jpeg
        if screenshot_data.startswith("data:image/png;base64,"):
            image_format = "image/png"
            image_data_b64 = screenshot_data.split(',')[1]
            file_extension = "png"
            logger.info("Detected image format: PNG from prefix")
        elif screenshot_data.startswith("data:image/jpeg;base64,"):
            image_format = "image/jpeg"
            image_data_b64 = screenshot_data.split(',')[1]
            file_extension = "jpg"
            logger.info("Detected image format: JPEG from prefix")
        elif screenshot_data.startswith("iVBORw0KGgo"):
            image_format = "image/png"
            image_data_b64 = screenshot_data
            file_extension = "png"
            logger.info("Detected image format: PNG from data")
        else:
            image_format = "image/jpeg"
            image_data_b64 = screenshot_data
            file_extension = "jpg"
            logger.info("Detected image format: JPEG (default)")

        # Save screenshot to file
        try:
            output_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/training_images/output_images_condition_stop_audience_page"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")[:-3]
            filename = f"screenshot_{timestamp}.{file_extension}"
            filepath = os.path.join(output_dir, filename)
            binary_data = base64.b64decode(image_data_b64)
            with open(filepath, 'wb') as f:
                f.write(binary_data)
            logger.info(f"Screenshot saved to file: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}\n{traceback.format_exc()}")
            # Continue even if saving fails
            
        # Prepare the prompt for Claude
        prompt = """
        You have perfect vision and pay great attention to detail which makes you an expert at counting details in table I want you to tell me everything that is written in the table and with all the columns. Write it down in free but neat text. Do you understand what I mean?

        You must only output the rows in the table. Without any additional words.

        For example:
        Lookalike (IL, 2%) - Similar Last 90 Days

        Type: Lookalike audience Similar Last 90 Days
        Availability: Audience not created (check ✓)
        Date created: 09/19/2023 10:09 AM
        Audience ID: 23859203708050523

        Just make sure the format is in json
        """
        logger.info("Prepared prompt for Claude Vision API")

        # Call Claude's Vision API
        try:
            logger.info("Calling Claude Vision API with screenshot data")
            logger.info(f"Using Claude model: claude-3-7-sonnet-20250219")
            logger.info(f"API parameters: max_tokens=20000, temperature=0.1")
            
            api_call_start = datetime.datetime.now()
            message = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=20000,
                temperature=0.1,
                messages=[                   
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": image_format,
                                    "data": image_data_b64
                                }
                            }
                        ]
                    }
                ]
            )
            api_call_end = datetime.datetime.now()
            api_call_duration = (api_call_end - api_call_start).total_seconds()
            
            logger.info(f"Claude Vision API call completed in {api_call_duration:.2f} seconds")
            
            # Extract the JSON response from Claude
            response_text = message.content[0].text
            response_length = len(response_text)
            logger.info(f"Received response from Claude: {response_length} characters")
            
            # Log a preview of the response (first 100 chars)
            response_preview = response_text[:100].replace('\n', ' ') + ("..." if len(response_text) > 100 else "")
            logger.info(f"Response preview: {response_preview}")
            
            # Parse the JSON from the response - extract the portion between ```json and ```
            logger.info("Attempting to extract JSON code block from response")
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            
            if json_match:
                json_content = json_match.group(1).strip()
                logger.info(f"Successfully extracted JSON code block: {len(json_content)} characters")
            else:
                # If no JSON code block found, try to use the entire response
                json_content = response_text.strip()
                logger.info(f"No JSON code block found, using entire response: {len(json_content)} characters")
            
            # Parse the JSON content
            try:
                logger.info("Attempting to parse JSON content")
                parsed_data = json.loads(json_content)
                logger.info(f"Successfully parsed JSON content")
                
                # Check if the parsed data is a list or contains audience_data
                if isinstance(parsed_data, list):
                    audience_entries = parsed_data
                    logger.info(f"Parsed data is a list with {len(audience_entries)} entries")
                elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
                    audience_entries = parsed_data.get("audience_data", [])
                    logger.info(f"Parsed data is an object with 'audience_data' field containing {len(audience_entries)} entries")
                else:
                    logger.error("Parsed data does not contain recognizable audience data format")
                    return ActionResult(error=f"Could not find audience data in Claude's response")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from Claude's response: {str(e)}")
                return ActionResult(error=f"Failed to parse JSON from Claude's response: {str(e)}")
            
            # Process Claude's response to extract audience data
            logger.info("Processing audience entries to standardize field names")
            audience_data = []
            for i, entry in enumerate(audience_entries):
                entry_id = entry.get("audience_id", "") or entry.get("Audience ID", "")
                entry_preview = f"Entry #{i+1}, ID: {entry_id}"
                logger.info(f"Processing {entry_preview}")
                
                # Check if entry already has capitalized field names
                if "Name" in entry and "Audience ID" in entry:
                    logger.info(f"{entry_preview}: Entry already has capitalized field names")
                    audience_data.append(entry)
                else:
                    # Ensure consistent field names with capitalization
                    logger.info(f"{entry_preview}: Converting to capitalized field names")
                    audience_entry = {
                        "Name": entry.get("Name", entry.get("name", "")),
                        "Type": entry.get("Type", entry.get("type", "")),
                        "Availability": entry.get("Availability", entry.get("availability", "")),
                        "Date created": entry.get("Date created", entry.get("date_created", "")),
                        "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
                    }
                    audience_data.append(audience_entry)
            
            logger.info(f"Processed {len(audience_data)} audience entries with standardized field names")
            
            # If not the first run, merge with existing data avoiding duplicates
            if not params.is_first_run and os.path.exists(file_path):
                try:
                    logger.info(f"Reading existing data from file: {file_path}")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                    
                    logger.info(f"Successfully read existing data: {len(existing_data)} entries")
                    
                    # Create a set of existing audience IDs for faster lookup
                    existing_ids = set()
                    for item in existing_data:
                        audience_id = item.get('Audience ID')
                        if audience_id:
                            existing_ids.add(audience_id)
                    
                    logger.info(f"Found {len(existing_ids)} unique audience IDs in existing data")
                    
                    # Add only new audience entries
                    duplicates_count = 0
                    new_entries_count = 0
                    
                    for item in audience_data:
                        audience_id = item.get('Audience ID')
                        if audience_id in existing_ids:
                            logger.info(f"Skipping duplicate audience ID: {audience_id}")
                            duplicates_count += 1
                        else:
                            logger.info(f"Adding new audience ID: {audience_id}")
                            existing_data.append(item)
                            new_entries_count += 1
                    
                    logger.info(f"Found {duplicates_count} duplicates and {new_entries_count} new entries")
                    
                    # Update the data to write
                    data_to_write = existing_data
                    logger.info(f"Final data to write: {len(data_to_write)} entries")
                except Exception as e:
                    error_msg = f"Failed to process existing data: {str(e)}"
                    logger.error(error_msg)
                    logger.error(f"Exception details: {traceback.format_exc()}")
                    return ActionResult(error=error_msg)
            else:
                # First run or file doesn't exist, use only new data
                if params.is_first_run:
                    logger.info("First run: using only new data")
                else:
                    logger.info(f"File does not exist at path {file_path}, using only new data")
                
                data_to_write = audience_data
                logger.info(f"Data to write: {len(data_to_write)} entries")
            
            # Write the data to the file
            logger.info(f"Writing data to file: {file_path}")
            file_write_start = datetime.datetime.now()
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data_to_write, f, indent=2, ensure_ascii=False)
                
                file_write_end = datetime.datetime.now()
                file_write_duration = (file_write_end - file_write_start).total_seconds()
                logger.info(f"Successfully wrote {len(data_to_write)} entries to file in {file_write_duration:.2f} seconds")
            except Exception as e:
                error_msg = f"Failed to write data to file: {str(e)}"
                logger.error(error_msg)
                logger.error(f"Exception details: {traceback.format_exc()}")
                return ActionResult(error=error_msg)
            
            # Return success message with file path for future reference
            message = f"📊 Successfully extracted audience data from table screenshot. Saved to: {file_path}"
            logger.info("Function completed successfully")
            logger.info(f"Final message: {message}")
            
            session_end_time = datetime.datetime.now()
            logger.info("="*80)
            logger.info(f"EXTRACTION SESSION COMPLETED: {session_end_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
            logger.info("="*80)
            
            return ActionResult(
                extracted_content=message,
                include_in_memory=True,
                metadata={"file_path": file_path, "entries_count": len(data_to_write)}
            )
            
        except Exception as e:
            error_msg = f"Error calling Claude Vision API: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Exception details: {traceback.format_exc()}")
            return ActionResult(error=error_msg)
        
    except Exception as e:
        error_message = f"Failed to extract audience data: {str(e)}"
        if logger: # Check if logger was initialized
            logger.error(error_message)
            logger.error(f"Exception details: {traceback.format_exc()}")
            
            session_end_time = datetime.datetime.now()
            logger.error("="*80)
            logger.error(f"EXTRACTION SESSION FAILED: {session_end_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
            logger.error("="*80)
        else:
            print(f"ERROR (Logger not initialized): {error_message}") # Fallback print
            print(traceback.format_exc())
        
        return ActionResult(error=error_message)
        
    finally: # Ensure handlers are closed/removed if logger was initialized
        if logger and file_handler:
            try:
                logger.removeHandler(file_handler)
                file_handler.close()
            except Exception as close_err:
                print(f"Error closing logger handler: {close_err}") # Non-critical, just print
