from browser_use import ActionResult
from browser_use.browser.context import BrowserContext
import os
import anthropic
import logging
import datetime
import re
import base64
import traceback
from dotenv import load_dotenv

async def perform_check_condition_stop_page_wheel(browser: BrowserContext) -> ActionResult:
    """
    Helper function containing the logic to analyze the current page screenshot 
    to determine whether to continue scrolling vertically or stop.
    
    Args:
        browser: Browser context instance to capture screenshot
        
    Returns:
        ActionResult: Contains decision (CONTINUE/STOP) and scroll parameter
    """
    try:
        # Set up logging
        log_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "scroll_condition_check.log")
        
        # Configure logger
        logger = logging.getLogger("scroll_condition_check")
        logger.setLevel(logging.DEBUG)
        
        # Prevent propagation to root logger (stops terminal output)
        logger.propagate = False
        
        # Remove existing handlers if any
        if logger.handlers:
            for handler in logger.handlers:
                logger.removeHandler(handler)
        
        # File handler for the log file
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter with detailed timestamp
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S.%f'
        )
        file_handler.setFormatter(formatter)
        
        # Add the file handler to the logger
        logger.addHandler(file_handler)
        
        # Start logging with session boundary and basic info
        session_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        logger.info("="*80)
        logger.info(f"STARTING NEW SCROLL CONDITION CHECK SESSION: {session_start_time}")
        logger.info("="*80)
        
        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded")
        
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
        
        # Detect image format
        if screenshot_data.startswith("iVBORw0KGgo"):
            image_format = "image/png"
            file_extension = "png"
            logger.info("Detected image format: PNG")
        else:
            image_format = "image/jpeg"
            file_extension = "jpg"
            logger.info("Detected image format: JPEG (default)")
        
        # Save screenshot to file with readable timestamp filename
        try:
            # Create output directory if it doesn't exist
            output_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/training_images/output_images_condition_stop_audience_page"
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Ensuring output directory exists: {output_dir}")
            
            # Generate a human-readable timestamp for the filename (YYYY-MM-DD_HH-MM-SS_mmm)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")[:-3]
            filename = f"screenshot_{timestamp}.{file_extension}"
            filepath = os.path.join(output_dir, filename)
            
            # Decode the base64 data back to binary
            # Remove the base64 prefix if present
            if "," in screenshot_data:
                image_data = screenshot_data.split(",")[1]
            else:
                image_data = screenshot_data
                
            # Decode the image data
            binary_data = base64.b64decode(image_data)
            
            # Write to file
            with open(filepath, 'wb') as f:
                f.write(binary_data)
                
            logger.info(f"Screenshot saved to file: {filepath}")
        except Exception as e:
            # Log error but continue with the function (don't break existing functionality)
            logger.error(f"Failed to save screenshot to file: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")
            logger.info("Continuing with function execution despite screenshot save error")
        
        # Load training images from directory
        training_images = []
        training_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/training_images/train-condition-scroll-audience-page"
        
        # Check if directory exists
        if os.path.exists(training_dir):
            logger.info(f"Loading training images from {training_dir}")
            try:
                # List and sort image files
                image_files = [f for f in os.listdir(training_dir) if f.lower().endswith('.png')]
                image_files.sort()  # Sort alphabetically
                
                logger.info(f"Found {len(image_files)} training images")
                
                # Load each image
                for img_file in image_files:
                    img_path = os.path.join(training_dir, img_file)
                    logger.info(f"Loading training image: {img_path}")
                    
                    try:
                        with open(img_path, 'rb') as f:
                            img_data = f.read()
                            # Convert to base64
                            img_base64 = base64.b64encode(img_data).decode('utf-8')
                            # Determine image type
                            img_type = "image/png" if img_file.lower().endswith('.png') else "image/jpeg"
                            # Add to training images
                            training_images.append({"media_type": img_type, "data": img_base64})
                            logger.info(f"Successfully loaded training image: {img_file}")
                    except Exception as e:
                        logger.error(f"Failed to load training image {img_file}: {str(e)}")
                        logger.error(f"Error details: {traceback.format_exc()}")
                
                logger.info(f"Successfully loaded {len(training_images)} training images")
            except Exception as e:
                logger.error(f"Error loading training images: {str(e)}")
                logger.error(f"Error details: {traceback.format_exc()}")
        else:
            logger.warning(f"Training directory does not exist: {training_dir}")
            logger.warning("Proceeding without training images")
        
        # Create the new system prompt
        system_prompt = """You have perfect vision and pay great attention to detail which makes you an expert at counting details in table and to know how to observe and understand exactly the state of the table's scroll bar.

        You are an AI assistant tasked with deciding whether to continue scrolling or stop scrolling the audience table on the Facebook advertising dashboard. Your decision should be based on the image description provided and the previous examples in the discussion.

        First, carefully analyze the following image description

        Now, consider the previous examples from the discussion:

        To make your decision, follow these steps:
        1. Examine the image description for key information about the audience table's current state.
        2. Compare the current state with the patterns and criteria established in the previous examples.
        3. Determine if the current state indicates that scrolling should continue or stop.

        When making your decision, consider factors such as:
        - Has the scroll bar reached the end of the scroll bar? If there is less than the height of the last row in the table left, then this is a sign that the scroll bar has reached the end, otherwise not.

        - Is the end of the scroll bar in front of the last row visible in the table? If so, then there is a stop, otherwise continue.



Instructions:
1. You identify the bottom of the audience table
2. You carefully analyze the position of the bottom edge of the scroll bar on the right in the screenshot and the distance from the bottom of the audience table
3. You calculate solely based on the screenshot analysis the number of rows between the bottom edge of the scroll bar and the bottom border of the audience table.
4. You decide according to the explanation in the xml tag called Calculate the parameter by the lines between the bottom edge of the scroll bar and the bottom border of the table

<Calculate the parameter by the lines between the bottom edge of the scroll bar and the bottom border of the table>
The parameters are calculated according to the following key:
1. If the distance between the bottom edge of the scroll bar and the bottom border of the table is in the region of 7 lines (meaning there are about 7 lines in the table between the bottom and the bottom border of the table) then you give permission for a scroll of 600px
2. If it is more than 7 lines then it is 600 px
3. If it is between 7 and 3 lines between the bottom edge of the scroll bar and the bottom border of the table then it is 500px.
4. If it is between 3 and 1 lines then it is 100px
5. If it is 1 and less than that then you issue STOP.

</Calculating the parameter by the rows between the bottom edge of the scroll bar and the bottom border of the table>



        Provide your decision and reasoning in the following format:
        <reasoning>
        [Explain your reasoning for the decision, Give a brief explanation and estimate of the distance of the top edge of the scroll bar from the top border of the table, give a brief explanation and estimate of the distance of the bottom edge of the scroll bar from the bottom border of the table, give a brief explanation of whether it is possible to scroll according to the distance data and whether you identify cut rows in the table, give a brief explanation of your decision to estimate the vertical parameter.]
        </reasoning>

        <decision>
        [Your decision: either "CONTINUE" or "STOP"] /n
        [Vertical scroll parameter: If it is STOP then the value NONE If it is CONTINUE then the value with px unit according to how you evaluate]
        </decision>




        When you come to estimate the vertical decision parameter, you consider the following data:

        - The height of each row in the table is 50px
        - If the scroll bar is at the beginning of the track then you can scroll 10 rows
- If the scroll bar is in the 50% area (i.e. the space from the top edge of the scroll bar to the top border of the table is more or less the same distance as the bottom edge of the scroll bar from the bottom border of the scroll track) then the scroll is 5 rows
        - When the bottom of the scroll bar is about a row and a half high from the table (you can see this in the image you receive and estimate it yourself) then the scroll is one and a half rows.

        To determine the size of the vertical decision parameter you take the following steps:
        1. You look carefully at the image you received and check the distance of the top edge of the scroll bar from the top border of the table. The reference you use to estimate this is the number of rows in the table that are between the top edge of the scroll bar and the top border of the table.
        2. You look carefully at the image you received and check the distance of the lower edge of the scroll bar from the lower border of the table. The reference that you use to estimate the number of rows in the table that are between the lower edge of the scroll bar and the lower border of the table.
        3. According to the results in the previous two sections, you know how to act on the data to estimate the vertical decision parameters




        General rules that you need to refer to in order to give an answer and create the reasoning:
        1. If there is no marking of the scroll bar's scroll path, then you know how to estimate the position in the path and the amount of way left to scroll relative to the bottom border of the table, which is marked by the lowest line in the table


        Remember, your goal is to make an appropriate decision based on the information provided in the image description and the patterns established in the previous examples."""
        
        logger.info("System prompt prepared")
        
        # Prepare the new message structure
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "\nBefore you start acting on your system prompt, I want to give you a few examples for calculating the number of rows in the table between the bottom edge of the scroll bar and the bottom border of the table. According to these examples, you will always be able to understand and use them when you need to calculate the number of rows for a new user query. Do you understand what I mean?\n\n\n\n\n\n"
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I understand completely. You want to provide me with examples that will help me better understand how to calculate the number of rows between the bottom edge of the scroll bar and the bottom border of the table. These examples will serve as reference points for when I need to make similar calculations in future queries. I'm ready to review these examples and apply the knowledge to any new scenarios you present."
                    }
                ]
            }
        ]
        
        # Initialize a counter for adding training images to messages
        image_counter = 0
        
        # Add Example 1
        if image_counter < len(training_images):
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": training_images[image_counter]["media_type"],
                            "data": training_images[image_counter]["data"]
                        }
                    },
                    {
                        "type": "text",
                        "text": "<Example 1 for calculating the number of rows>\nWhat is the number of rows between the bottom edge of the scroll bar and the bottom border of the table?"
                    }
                ]
            })
            
            messages.append({
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "<reasoning>\nI am an expert at distinguishing details in a screenshot of the Audiences dashboard on the Facebook Advertising dashboard.\n\nI see that the bottom edge of the gray scroll bar on the right side of the screen is opposite the value 23857669590730523 of the audience id column in the table in the screenshot.\n\nTherefore, the row with the id number 23857669590730523 is the row on which the bottom edge of the scroll bar is located.\n\nSo when I look at the screenshot again very, very carefully, I see that there are 6 rows below row 23857669590730523.\n\nI know there are 6 rows because I see that there are 6 more different values ​​below the row with the id 23857669590730523.\n\nSo according to the system prompt and according to the instructions where the xml tag is called Calculate the parameter by the lines between the bottom edge of the scroll bar and the bottom border of the table, then according to section 3 you need 500px to continue scrolling down.\n</reasoning>\n\n<decision>\nCONTINUE\n500px\n</decision>"
                    }
                ]
            })
            
            image_counter += 1
            logger.info(f"Added Example 1 to messages with training image {image_counter}")
        
        # Add Example 2
        if image_counter < len(training_images):
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "<Example 2"
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": training_images[image_counter]["media_type"],
                            "data": training_images[image_counter]["data"]
                        }
                    },
                    {
                        "type": "text",
                        "text": " for calculating the number of rows>\nWhat is the number of rows between the bottom edge of the scroll bar and the bottom border of the table?"
                    }
                ]
            })
            
            messages.append({
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "<reasoning>\nI am an expert at distinguishing details in a screenshot of the Audiences dashboard on the Facebook Advertising dashboard.\n\nI see that the bottom edge of the gray scroll bar on the right side of the screen is opposite the value 23857301447110523 of the audience id column in the table in the screenshot.\n\nTherefore, the row with the id number 23857301447110523 is the row on which the bottom edge of the scroll bar is located.\n\nSo when I look at the screenshot again very, very carefully, I see that there are 1.5 rows below row 23857301447110523.\n\nI know there are 1.5 rows because I see that there are 1.5 more different values ​​below the row with the id 23857301447110523.\n\nSo according to the system prompt and according to the instructions where the xml tag is called Calculate the parameter by the lines between the bottom edge of the scroll bar and the bottom border of the table, then according to section 3 you need 100px to continue scrolling down.\n</reasoning>\n\n<decision>\nCONTINUE\n100px\n</decision>"
                    }
                ]
            })
            
            image_counter += 1
            logger.info(f"Added Example 2 to messages with training image {image_counter}")
        
        # Add Example 3
        if image_counter < len(training_images):
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "<Example 3 for calculating the number of rows>\nWhat is the number of rows between the bottom edge of the scroll bar and the bottom border of the table?\n"
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": training_images[image_counter]["media_type"],
                            "data": training_images[image_counter]["data"]
                        }
                    }
                ]
            })
            
            messages.append({
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "<reasoning>\nI am an expert at distinguishing details in a screenshot of the Audiences dashboard on the Facebook Advertising dashboard.\n\nI see that the bottom edge of the gray scroll bar on the right side of the screen is opposite the value 23857301441360523 of the audience id column in the table in the screenshot.\n\nTherefore, the row with the id number 23857301441360523 is the row on which the bottom edge of the scroll bar is located.\n\nSo when I look at the screenshot again very, very carefully, I see that there are 1.5 rows below row 23857301441360523.\n\nI know there are 1.5 rows because I see that there are 1.5 more different values ​​below the row with the id 23857301441360523.\n\nSo according to the system prompt and according to the instructions where the xml tag is called Calculate the parameter by the lines between the bottom edge of the scroll bar and the bottom border of the table, then according to section 3 you need 100px to continue scrolling down.\n</reasoning>\n\n<decision>\nCONTINUE\n100px\n</decision>"
                    }
                ]
            })
            
            image_counter += 1
            logger.info(f"Added Example 3 to messages with training image {image_counter}")
        
        # Add Example 4
        if image_counter < len(training_images):
            messages.append({
                "role": "user",
                "content": [
                {
                    "type": "text",
                        "text": "<Example 4 for calculating the number of rows>\nWhat is the number of rows between the bottom edge of the scroll bar and the bottom border of the table?\n\n"
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                            "media_type": training_images[image_counter]["media_type"],
                            "data": training_images[image_counter]["data"]
                        }
                    }
                ]
            })
            
            messages.append({
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "<reasoning>\nI am an expert at distinguishing details in a screenshot of the Audiences dashboard on the Facebook Advertising dashboard.\n\nLooking at the image carefully, I can see that the bottom edge of the gray scroll bar on the right side of the screen is positioned approximately opposite the value 23857301436680523 of the audience ID column in the table.\n\nTherefore, the row with the ID number 23857301436680523 is the row on which the bottom edge of the scroll bar is located.\n\nWhen I examine the screenshot very carefully, I can see that there is less than 1 row below the row with ID 23857301436680523. In fact, it appears to be the last visible row in the table, with perhaps a small portion of another row partially visible below it.\n\nSince there is less than 1 row between the bottom edge of the scroll bar and the bottom border of the table, according to the system prompt instructions in section 5 of the \"Calculate the parameter by the lines between the bottom edge of the scroll bar and the bottom border of the table\" tag, I need to issue a STOP command.\n</reasoning>\n\n<decision>\nSTOP\nNONE\n</decision>"
                    }
                ]
            })
            
            image_counter += 1
            logger.info(f"Added Example 4 to messages with training image {image_counter}")
        
        # Add Example 5
        if image_counter < len(training_images):
            messages.append({
                "role": "user",
                "content": [
                {
                    "type": "text",
                        "text": "<Example 5 for calculating the number of rows>\nWhat is the number of rows between the bottom edge of the scroll bar and the bottom border of the table?\n\n"
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                            "media_type": training_images[image_counter]["media_type"],
                            "data": training_images[image_counter]["data"]
                        }
                    }
                ]
            })
            
            messages.append({
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "<reasoning>\nI am an expert at distinguishing details in a screenshot of the Audiences dashboard on the Facebook Advertising dashboard.\n\nI see that the bottom edge of the gray scroll bar on the right side of the screen is opposite the value 23857893763360523 of the audience id column in the table in the screenshot.\n\nTherefore, the row with the id number 23857893763360523 is the row on which the bottom edge of the scroll bar is located.\n\nSo when I look at the screenshot again very, very carefully, I see that there are 7 rows below row 23857893763360523.\n\nI know there are7 rows because I see that there are 7 more different values ​​below the row with the id 23857893763360523.\n\nSo according to the system prompt and according to the instructions where the xml tag is called Calculate the parameter by the lines between the bottom edge of the scroll bar and the bottom border of the table, then according to section 3 you need 600px to continue scrolling down.\n</reasoning>\n\n<decision>\nCONTINUE\n600px\n</decision>"
                    }
                ]
            })
            
            image_counter += 1
            logger.info(f"Added Example 5 to messages with training image {image_counter}")
        
        # Add the final user message with the current screenshot
        messages.append({
            "role": "user",
            "content": [
            {
                "type": "text",
                    "text": "You have perfect vision and pay great attention to detail\n\nWhat is the number of rows between the bottom edge of the scroll bar and the bottom border of the table?\n\nI want you to answer the question based on the mimicry in the examples and while understanding the pattern from the examples between the screenshot in the examples and the bottom edge of the scroll bar. From this understanding, you answer the question I asked regarding the current screenshot.\n"
            },
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_format,
                    "data": screenshot_data
                }
            }
        ]
        })
        
        logger.info(f"Prepared {len(messages)} messages for Claude API")
        
        # Call Claude's Vision API with the new implementation
        try:
            logger.info("Calling Claude Vision API with screenshot and training data")
            logger.info(f"Using Claude model: claude-3-7-sonnet-20250219")
            logger.info(f"API parameters: max_tokens=20000, temperature=0.5")
            
            api_call_start = datetime.datetime.now()
            
            # The new API call implementation
            message = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=20000,
                temperature=0.5,
                system=system_prompt,
                messages=messages
            )
            
            api_call_end = datetime.datetime.now()
            api_call_duration = (api_call_end - api_call_start).total_seconds()
            
            logger.info(f"Claude Vision API call completed in {api_call_duration:.2f} seconds")
            
            # Extract the response from Claude
            response_text = message.content[0].text
            response_length = len(response_text)
            logger.info(f"Received response from Claude: {response_length} characters")
            
            # Log a preview of the response (first 100 chars)
            response_preview = response_text[:100].replace('\n', ' ') + ("..." if len(response_text) > 100 else "")
            logger.info(f"Response preview: {response_preview}")
            
            # Log the full response with proper formatting
            logger.info("="*80)
            logger.info("===== BEGINNING OF FULL CLAUDE RESPONSE =====")
            logger.info("-"*80)
            # Split the response by lines and log each line separately to maintain formatting
            for i, line in enumerate(response_text.split('\n'), 1):
                logger.info(f"CLAUDE[{i:03d}]: {line}")
            logger.info("-"*80)
            logger.info("===== END OF FULL CLAUDE RESPONSE =====")
            logger.info("="*80)
            
            # Parse the response to extract decision and scroll parameter
            # Extract the reasoning and decision sections
            reasoning_match = re.search(r'<reasoning>(.*?)</reasoning>', response_text, re.DOTALL)
            decision_match = re.search(r'<decision>(.*?)</decision>', response_text, re.DOTALL)
            
            if not reasoning_match or not decision_match:
                logger.error("Failed to extract reasoning or decision from Claude's response")
                return ActionResult(error="Failed to parse Claude's response: Could not find reasoning or decision sections")
            
            reasoning = reasoning_match.group(1).strip()
            decision_text = decision_match.group(1).strip()
            
            logger.info(f"Extracted reasoning: {len(reasoning)} characters")
            logger.info(f"Extracted decision: {decision_text}")
            
            # Extract the decision (CONTINUE or STOP) and scroll parameter
            decision_lines = decision_text.split('\n')
            if len(decision_lines) < 2:
                logger.error(f"Decision section did not contain expected format: {decision_text}")
                return ActionResult(error="Failed to parse decision: Invalid format")
            
            decision = decision_lines[0].strip()
            scroll_param = decision_lines[1].strip()
            
            logger.info(f"Parsed decision: {decision}")
            logger.info(f"Parsed scroll parameter: {scroll_param}")
            
            # Validate the decision
            if decision not in ["CONTINUE", "STOP"]:
                logger.error(f"Invalid decision value: {decision}")
                return ActionResult(error=f"Invalid decision value: {decision}")
            
            # Validate and process the scroll parameter
            scroll_value = None
            if decision == "CONTINUE":
                # Extract numeric value from the scroll parameter (e.g., "350 px" -> 350)
                scroll_match = re.search(r'(\d+)\s*px', scroll_param)
                if not scroll_match:
                    logger.error(f"Could not extract scroll value from: {scroll_param}")
                    scroll_value = 100  # Default value if parsing fails
                    logger.info(f"Using default scroll value: {scroll_value}")
                else:
                    scroll_value = int(scroll_match.group(1))
                    logger.info(f"Extracted scroll value: {scroll_value}")
            else:  # STOP case
                if scroll_param != "NONE":
                    logger.warning(f"Unexpected scroll parameter for STOP decision: {scroll_param}")
                scroll_value = 0
                logger.info("Scroll value set to 0 for STOP decision")
            
            # Create a user-friendly message
            if decision == "CONTINUE":
                message = f"🖱️ Analysis indicates scrolling should CONTINUE with {scroll_value}px"
            else:
                message = "🛑 Analysis indicates scrolling should STOP (end of content reached)"
            
            # Log the final result
            logger.info(f"Final decision: {decision}, scroll value: {scroll_value}")
            logger.info(f"Final message: {message}")
            
            session_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            logger.info("="*80)
            logger.info(f"SCROLL CONDITION CHECK SESSION COMPLETED: {session_end_time}")
            logger.info("="*80)
            
            # Return the result
            return ActionResult(
                extracted_content=message,
                include_in_memory=True,
                metadata={
                    "decision": decision,
                    "scroll_value": scroll_value,
                    "reasoning": reasoning
                }
            )
            
        except Exception as e:
            error_msg = f"Error calling Claude Vision API: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Exception details: {traceback.format_exc()}")
            return ActionResult(error=error_msg)
        
    except Exception as e:
        try:
            # Try to log the error if logger is defined
            error_message = f"Failed to check scroll condition: {str(e)}"
            if 'logger' in locals():
                logger.error(error_message)
                logger.error(f"Exception details: {traceback.format_exc()}")
                
                session_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                logger.error("="*80)
                logger.error(f"SCROLL CONDITION CHECK SESSION FAILED: {session_end_time}")
                logger.error("="*80)
        except:
            # If logging itself fails, just continue to return the error
            pass
            
        return ActionResult(error=error_message) 