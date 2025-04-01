# Implementation Plan for check_condition_stop_page_wheel Function

## Overview
This markdown Document outlines a detailed implementation plan for adding a new function called `check_condition_stop_page_wheel` to the `custom_controller.py` file. This function will help the agent determine whether to continue scrolling vertically or stop based on screenshot analysis using Claude's Vision API.

## Implementation Checklist

### 1. Function Setup and Integration
- [ ] Define function signature with appropriate parameters (browser: BrowserContext)
- [ ] Add appropriate decorator using controller.action
- [ ] Create proper class model for function parameters if needed
- [ ] Include comprehensive docstring explaining function purpose and usage

### 2. Logging Setup
- [ ] Configure logger with appropriate name ("scroll_condition_check")
- [ ] Set up log file path in '/Users/meirsabag/Public/browser_use_ver4_newVersion/logs'
- [ ] Create log formatter with detailed timestamp
- [ ] Add session boundary markers in logs
- [ ] Log function parameters and execution steps
- [ ] Configure proper log levels (INFO, DEBUG, ERROR)

### 3. Environment Setup
- [ ] Load environment variables (dotenv)
- [ ] Retrieve ANTHROPIC_API_KEY from environment variables
- [ ] Initialize Anthropic client with API key
- [ ] Log successful initialization of client

### 4. Screenshot Capture
- [ ] Get current page from browser context
- [ ] Take a screenshot of the current page
- [ ] Measure and log screenshot capture time
- [ ] Determine image format (PNG or JPEG)
- [ ] Check screenshot data validity and size
- [ ] Log successful screenshot capture

### 5. Image Processing
- [ ] Setup directory path for training images
- [ ] Load training images in correct sequence (1.jpg, 2.jpg, etc.)
- [ ] Convert training images to base64 format
- [ ] Determine correct media type for each image
- [ ] Prepare complete array of messages with correct image data

### 6. Claude Vision API Integration
- [ ] Prepare system prompt exactly as specified
- [ ] Format user messages with correct image data insertion
- [ ] Replace final message's image data with the captured screenshot
- [ ] Call Claude Vision API with appropriate parameters
- [ ] Measure and log API call duration
- [ ] Handle API call errors with appropriate error messages

### 7. Response Processing
- [ ] Extract text response from Claude's message
- [ ] Parse to find decision (CONTINUE/STOP)
- [ ] Extract scroll parameter value (if CONTINUE)
- [ ] Log decision and parameters
- [ ] Format extracted data for return value

### 8. Error Handling
- [ ] Implement try/except blocks around major operations
- [ ] Add specific error handling for screenshot capture failures
- [ ] Add specific error handling for API call failures
- [ ] Add specific error handling for response parsing failures
- [ ] Log detailed error information including tracebacks
- [ ] Return appropriate error messages in ActionResult

### 9. Return Value Preparation
- [ ] Create ActionResult with extracted content
- [ ] Include decision (CONTINUE/STOP) in metadata
- [ ] Include scroll parameter (if applicable) in metadata
- [ ] Set include_in_memory flag appropriately
- [ ] Log final result being returned

### 10. Testing and Validation
- [ ] Review code for consistency with codebase patterns
- [ ] Check parameter naming conventions match existing code
- [ ] Verify error handling follows codebase patterns
- [ ] Ensure logging details match existing functions
- [ ] Verify ActionResult format matches expectations

## Critical Implementation Details

### Claude API Call Format
The function must follow the exact LLM calling format provided, with these key components:
- Use model "claude-3-5-sonnet-20241022"
- Set max_tokens to 8192
- Set temperature to 0.1
- Insert the system prompt exactly as provided
- Populate all image data fields correctly
- For the final message, replace image data with the captured screenshot

### Training Images Path
Training images are located at:
`/Users/meirsabag/Public/browser_use_ver4_newVersion/training_images/train-condition-scroll-audience-page`

### Screenshot Format
Screenshot must be:
- Full page capture
- Base64 encoded
- Correctly identified as PNG or JPEG format
- Properly inserted into the final message's image data field

### Response Parsing
The function must correctly parse Claude's response to extract:
1. Decision: CONTINUE or STOP
2. Scroll parameter: Pixel value (e.g., "350px") or NONE

### ActionResult Format
The return value should include:
- Extracted content: The decision and reasoning
- Metadata: Should include decision and scroll parameter
- include_in_memory: Set to true 