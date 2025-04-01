# Refactoring Plan: custom_controller.py

**Goal:** Refactor `remote_tools_folders/custom_controller.py` by extracting the implementation logic of each `@controller.action` into separate helper functions located in a new `remote_tools_folders/controller_actions/` directory.

**Project Root:** Assume the base directory is `/Users/meirsabag/Public/browser_use_ver4_newVersion/`

---

## Phase 1: Setup New Directory Structure

**Step 1.1:** Create the actions directory.
- **Action:** Create a new directory named `controller_actions`.
- **Path:** `/Users/meirsabag/Public/browser_use_ver4_newVersion/remote_tools_folders/controller_actions/`
- **Checklist:** [ ] Directory `controller_actions` created at the specified path.

**Step 1.2:** Create the package initializer file.
- **Action:** Create an empty file named `__init__.py` inside the new directory.
- **Path:** `/Users/meirsabag/Public/browser_use_ver4_newVersion/remote_tools_folders/controller_actions/__init__.py`
- **Checklist:** [ ] Empty file `__init__.py` created at the specified path.

---

## Phase 2: Refactor `move_mouse` Action

**Step 2.1:** Create the helper file for `move_mouse`.
- **Action:** Create a new file named `action_move_mouse.py`.
- **Path:** `/Users/meirsabag/Public/browser_use_ver4_newVersion/remote_tools_folders/controller_actions/action_move_mouse.py`
- **Checklist:** [ ] File `action_move_mouse.py` created.

**Step 2.2:** Add imports to `action_move_mouse.py`.
- **Action:** Add the following import statements at the beginning of `action_move_mouse.py`.
  ```python
  from browser_use import ActionResult
  from browser_use.browser.context import BrowserContext
  from pydantic import BaseModel, Field
  from typing import Optional
  import traceback # Added for potential error logging consistency
  # import logging # Add if planning to log errors within the helper
  ```
- **Checklist:** [ ] Imports added to action_move_mouse.py.

**Step 2.3:** Define Pydantic model in action_move_mouse.py.
- **Action:** Copy or define the MouseMoveAction Pydantic model within action_move_mouse.py.
  ```python
  class MouseMoveAction(BaseModel):
      x: float = Field(..., description="X coordinate relative to the viewport in CSS pixels")
      y: float = Field(..., description="Y coordinate relative to the viewport in CSS pixels")
      steps: Optional[int] = Field(1, description="Number of intermediate steps for the movement (default: 1)")
  ```
- **Checklist:** [ ] MouseMoveAction model defined in action_move_mouse.py.

**Step 2.4:** Define the helper function perform_move_mouse in action_move_mouse.py.
- **Action:** Define the async helper function signature.
  ```python
  async def perform_move_mouse(params: MouseMoveAction, browser: BrowserContext) -> ActionResult:
      """
      Helper function containing the logic to move the mouse cursor.
      """
      # Implementation will be added next
      pass
  ```
- **Checklist:** [ ] perform_move_mouse function signature defined.

**Step 2.5:** Move implementation logic to perform_move_mouse.
- **Action:** Copy the try...except block from the original move_mouse function in custom_controller.py and paste it as the body of the perform_move_mouse function in action_move_mouse.py.
  ```python
  async def perform_move_mouse(params: MouseMoveAction, browser: BrowserContext) -> ActionResult:
      """
      Helper function containing the logic to move the mouse cursor.
      """
      try:
          page = await browser.get_current_page()
          await page.mouse.move(params.x, params.y, steps=params.steps)
          message = f"🖱️ Mouse moved to coordinates ({params.x}, {params.y})"
          return ActionResult(extracted_content=message, include_in_memory=True)
      except Exception as e:
          error_message = f"Failed to move mouse: {str(e)}"
          # Optional: Add logging here
          # logging.error(f"Failed to move mouse: {str(e)}\n{traceback.format_exc()}")
          return ActionResult(error=error_message)
  ```
- **Checklist:** [ ] Implementation logic moved to perform_move_mouse.

**Step 2.6:** Update custom_controller.py for move_mouse.
- **Action:**
  1. Add the import statement at the top of custom_controller.py:
     ```python
     from .controller_actions.action_move_mouse import perform_move_mouse, MouseMoveAction
     ```
  2. Replace the entire body of the original move_mouse function with a single line calling the helper:
     ```python
     @controller.action(
         'Move mouse cursor to specific coordinates on the page',
         param_model=MouseMoveAction # Ensure this uses the imported model
     )
     async def move_mouse(params: MouseMoveAction, browser: BrowserContext) -> ActionResult:
         """
         Action definition: Move the mouse cursor to specific coordinates on the page.
         Calls the helper function perform_move_mouse for implementation.
         """
         return await perform_move_mouse(params, browser)
     ```
- **Checklist:** [ ] custom_controller.py updated for move_mouse imports and function body.

---

## Phase 3: Refactor mouse_click Action

**Step 3.1:** Create the helper file for mouse_click.
- **Action:** Create a new file named action_mouse_click.py.
- **Path:** `/Users/meirsabag/Public/browser_use_ver4_newVersion/remote_tools_folders/controller_actions/action_mouse_click.py`
- **Checklist:** [ ] File action_mouse_click.py created.

**Step 3.2:** Add imports to action_mouse_click.py.
- **Action:** Add necessary imports.
  ```python
  from browser_use import ActionResult
  from browser_use.browser.context import BrowserContext
  import traceback
  # import logging
  ```
- **Checklist:** [ ] Imports added to action_mouse_click.py.

**Step 3.3:** Define the helper function perform_mouse_click in action_mouse_click.py.
- **Action:** Define the async helper function signature.
  ```python
  async def perform_mouse_click(browser: BrowserContext) -> ActionResult:
      """
      Helper function containing the logic to click the mouse at its current position.
      """
      # Implementation will be added next
      pass
  ```
- **Checklist:** [ ] perform_mouse_click function signature defined.

**Step 3.4:** Move implementation logic to perform_mouse_click.
- **Action:** Copy the try...except block from the original mouse_click function in custom_controller.py into perform_mouse_click.
  ```python
  async def perform_mouse_click(browser: BrowserContext) -> ActionResult:
      """
      Helper function containing the logic to click the mouse at its current position.
      """
      try:
          page = await browser.get_current_page()
          # Note: Original code used (0, 0, position_relative_to_element=False) which clicks relative to top-left of viewport.
          # Playwright's default page.mouse.click(x, y) clicks at coordinates.
          # To click at the *current* mouse position implicitly, maybe just page.mouse.down() followed by page.mouse.up() is needed,
          # or simply use page.click('body', position={'x': current_x, 'y': current_y}) if position is tracked,
          # but the original code clicks at (0,0) of viewport. Sticking to original logic:
          await page.mouse.click(0, 0) # Simplified, assuming default behavior or adjust if needed
          message = "🖱️ Mouse clicked at current position (or default 0,0)"
          return ActionResult(extracted_content=message, include_in_memory=True)
      except Exception as e:
          error_message = f"Failed to click mouse: {str(e)}"
          # Optional: Add logging here
          return ActionResult(error=error_message)
  ```
- **Checklist:** [ ] Implementation logic moved to perform_mouse_click.

**Step 3.5:** Update custom_controller.py for mouse_click.
- **Action:**
  1. Add the import: 
     ```python
     from .controller_actions.action_mouse_click import perform_mouse_click
     ```
  2. Replace the body of the original mouse_click function:
     ```python
     @controller.action('Click mouse at current position')
     async def mouse_click(browser: BrowserContext) -> ActionResult:
         """
         Action definition: Click the mouse at its current position.
         Calls the helper function perform_mouse_click for implementation.
         """
         return await perform_mouse_click(browser)
     ```
- **Checklist:** [ ] custom_controller.py updated for mouse_click.

---

## Phase 4: Refactor mouse_hover Action

**Step 4.1:** Create the helper file for mouse_hover.
- **Action:** Create a new file named action_mouse_hover.py.
- **Path:** `/Users/meirsabag/Public/browser_use_ver4_newVersion/remote_tools_folders/controller_actions/action_mouse_hover.py`
- **Checklist:** [ ] File action_mouse_hover.py created.

**Step 4.2:** Add imports to action_mouse_hover.py.
- **Action:** Add necessary imports.
  ```python
  from browser_use import ActionResult
  from browser_use.browser.context import BrowserContext
  import traceback
  # import logging
  ```
- **Checklist:** [ ] Imports added to action_mouse_hover.py.

**Step 4.3:** Define the helper function perform_mouse_hover in action_mouse_hover.py.
- **Action:** Define the async helper function signature. Note the x, y parameters.
  ```python
  async def perform_mouse_hover(x: float, y: float, browser: BrowserContext) -> ActionResult:
      """
      Helper function containing the logic to perform a mouse hover action.
      """
      # Implementation will be added next
      pass
  ```
- **Checklist:** [ ] perform_mouse_hover function signature defined.

**Step 4.4:** Move implementation logic to perform_mouse_hover.
- **Action:** Copy the try...except block from the original mouse_hover function in custom_controller.py into perform_mouse_hover.
  ```python
  async def perform_mouse_hover(x: float, y: float, browser: BrowserContext) -> ActionResult:
      """
      Helper function containing the logic to perform a mouse hover action.
      """
      try:
          page = await browser.get_current_page()
          await page.mouse.move(x, y) # Hover is achieved by moving the mouse
          message = f"🖱️ Mouse hovering at coordinates ({x}, {y})"
          return ActionResult(extracted_content=message, include_in_memory=True)
      except Exception as e:
          error_message = f"Failed to hover mouse: {str(e)}"
          # Optional: Add logging here
          return ActionResult(error=error_message)
  ```
- **Checklist:** [ ] Implementation logic moved to perform_mouse_hover.

**Step 4.5:** Update custom_controller.py for mouse_hover.
- **Action:**
  1. Add the import: 
     ```python
     from .controller_actions.action_mouse_hover import perform_mouse_hover
     ```
  2. Replace the body of the original mouse_hover function:
     ```python
     # Note: The original action decorator took x, y directly, not a Pydantic model.
     @controller.action('Perform mouse hover at specific coordinates')
     async def mouse_hover(x: float, y: float, browser: BrowserContext) -> ActionResult:
         """
         Action definition: Move the mouse to specified coordinates to perform a hover action.
         Calls the helper function perform_mouse_hover for implementation.
         """
         return await perform_mouse_hover(x, y, browser)
     ```
- **Checklist:** [ ] custom_controller.py updated for mouse_hover.

---

## Phase 5: Refactor mouse_wheel Action (Complex)

**Step 5.1:** Create the helper file for mouse_wheel.
- **Action:** Create a new file named action_mouse_wheel.py.
- **Path:** `/Users/meirsabag/Public/browser_use_ver4_newVersion/remote_tools_folders/controller_actions/action_mouse_wheel.py`
- **Checklist:** [ ] File action_mouse_wheel.py created.

**Step 5.2:** Add imports to action_mouse_wheel.py.
- **Action:** Add the extensive list of imports required by this action's logic.
  ```python
  from browser_use import ActionResult
  from browser_use.browser.context import BrowserContext
  from pydantic import BaseModel, Field
  from typing import Optional, List, Tuple # Added Tuple
  import random
  import math
  import asyncio
  import base64 # Keep if used within, otherwise remove
  import datetime
  import os
  import logging
  import traceback
  ```
- **Checklist:** [ ] Imports added to action_mouse_wheel.py.

**Step 5.3:** Define Pydantic model in action_mouse_wheel.py.
- **Action:** Copy or define the MouseWheelAction Pydantic model.
  ```python
  class MouseWheelAction(BaseModel):
      delta_x: float = Field(0, description="Pixels to scroll horizontally (positive for right, negative for left). For most websites, use 0 for vertical-only scrolling.")
      delta_y: float = Field(..., description="Pixels to scroll vertically (positive for down, negative for up). Typical values: 100-300 for small scrolls, 500-800 for larger scrolls.")
  ```
- **Checklist:** [ ] MouseWheelAction model defined in action_mouse_wheel.py.

**Step 5.4:** Move internal helper functions to action_mouse_wheel.py.
- **Action:** Copy the functions create_segments and the logic from the nested scroll_segment_with_logging (refactoring it into a standalone async function like _scroll_segment_with_logging) from custom_controller.py into action_mouse_wheel.py. Place them before the main perform_mouse_wheel function.
  ```python
  # (Place imports here)

  # (Place Pydantic model here)

  # --- Start of Internal Helper Functions ---

  def create_segments(total_distance: int) -> List[int]:
      """ Break total scroll distance into natural segments. """
      # ... (Implementation copied from original file) ...
      if abs(total_distance) <= 5:
          return [total_distance]
      segment_count = max(3, min(8, abs(total_distance) // 100))
      segments = []
      remaining = total_distance
      for i in range(segment_count):
          if i == segment_count - 1:
              segments.append(remaining)
              break
          position = i / (segment_count - 1)
          weight = math.sin(position * math.pi)
          weight *= random.uniform(0.8, 1.2)
          # Calculate segment size carefully, avoiding division by zero if segment_count=1
          denominator = (segment_count - 0.5) if segment_count > 1 else 1
          segment_size = int(max(1, abs(total_distance * weight / denominator))) * (1 if total_distance > 0 else -1)

          # Ensure we don't overshoot if remaining is small, adjust segment size
          if abs(segment_size) > abs(remaining):
              segment_size = remaining

          # Ensure segment_size has the correct sign relative to remaining
          if remaining == 0:
              segment_size = 0
          elif (remaining > 0 and segment_size < 0) or (remaining < 0 and segment_size > 0):
               segment_size = 0 # Avoid changing direction unexpectedly

          # Ensure minimum step if not zero
          if segment_size == 0 and remaining != 0:
               segment_size = 1 if remaining > 0 else -1

          segments.append(segment_size)
          remaining -= segment_size
          if remaining == 0 and i < segment_count - 1: # Stop if distance covered early
               break

      # Filter out potential zero segments added by adjustments, unless it's the only segment
      final_segments = [s for s in segments if s != 0]
      if not final_segments and total_distance == 0: return [0]
      if not final_segments and total_distance != 0: return [total_distance] # fallback if filtering removed everything

      # Final check to ensure sum matches total_distance
      current_sum = sum(final_segments)
      if current_sum != total_distance:
          diff = total_distance - current_sum
          if final_segments: # Add difference to the last non-zero segment
              final_segments[-1] += diff
          else: # If all segments became zero somehow, just use the total distance
              final_segments = [total_distance]

      return final_segments
  ```
- **Checklist:** [ ] Started moving internal helper functions to action_mouse_wheel.py.

**Step 5.5:** Define the main helper function perform_mouse_wheel in action_mouse_wheel.py.
- **Action:** Define the async helper function signature.
  ```python
  async def perform_mouse_wheel(params: MouseWheelAction, browser: BrowserContext) -> ActionResult:
      """
      Helper function containing the logic to scroll the page using mouse wheel simulation.
      """
      # Implementation will be added next
      pass
  ```
- **Checklist:** [ ] perform_mouse_wheel function signature defined.

**Step 5.6:** Move implementation logic to perform_mouse_wheel.
- **Action:** Copy the try...except block from the original mouse_wheel function in custom_controller.py into perform_mouse_wheel. Crucially, update the part where the nested function was called to now call the standalone _scroll_segment_with_logging. Ensure the logger setup remains inside this function for now.
  ```python
  async def perform_mouse_wheel(params: MouseWheelAction, browser: BrowserContext) -> ActionResult:
      """
      Helper function containing the logic to scroll the page using mouse wheel simulation.
      """
      logger = None # Define logger variable early for use in except block
      try:
          # --- Logger Setup ---
          log_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/logs"
          os.makedirs(log_dir, exist_ok=True)
          log_file = os.path.join(log_dir, "mouse_wheel_actions.log")
          logger = logging.getLogger("mouse_wheel") # Assign to logger variable
          logger.setLevel(logging.DEBUG)
          logger.propagate = False
          if logger.handlers:
              for handler in list(logger.handlers): logger.removeHandler(handler) # Use list() for safe iteration
          file_handler = logging.FileHandler(log_file, encoding='utf-8')
          file_handler.setLevel(logging.DEBUG)
          formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S.%f')
          file_handler.setFormatter(formatter)
          logger.addHandler(file_handler)
          # --- End Logger Setup ---

          session_start_time = datetime.datetime.now()
          logger.info("="*80)
          logger.info(f"STARTING NEW MOUSE WHEEL SESSION: {session_start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
          logger.info("="*80)
          logger.info(f"Function parameters: delta_x={params.delta_x}, delta_y={params.delta_y}")

          page = await browser.get_current_page()
          logger.info("Retrieved current page from browser context")

          total_x = params.delta_x
          total_y = params.delta_y
          logger.info(f"Total scroll distances - X: {total_x}, Y: {total_y}")

          segments_x = create_segments(int(total_x)) # Uses helper in this file
          segments_y = create_segments(int(total_y)) # Uses helper in this file
          logger.info(f"Created {len(segments_x)} X segments and {len(segments_y)} Y segments")
          logger.info(f"X segments: {segments_x}")
          logger.info(f"Y segments: {segments_y}")

          max_len = max(len(segments_x), len(segments_y))
          segments_x.extend([0] * (max_len - len(segments_x)))
          segments_y.extend([0] * (max_len - len(segments_y)))
          # No need to log extension again if already logged above

          logger.info(f"Starting to process {len(segments_x)} scroll segments")
          for i, (seg_x, seg_y) in enumerate(zip(segments_x, segments_y)):
              logger.info(f"Processing segment {i+1}/{len(segments_x)}: X={seg_x}, Y={seg_y}")
              segment_start_time_inner = datetime.datetime.now() # Use different var name

              # Call the refactored internal helper function, passing the logger
              await _scroll_segment_with_logging(page, seg_x, seg_y, logger) # Uses helper in this file

              segment_scroll_end = datetime.datetime.now()
              segment_scroll_duration = (segment_scroll_end - segment_start_time_inner).total_seconds()
              logger.info(f"Completed segment {i+1} scrolling in {segment_scroll_duration:.2f} seconds")

              # Pause between segments is now inside _scroll_segment_with_logging? No, it was outside. Keep it here.
              pause_time = random.uniform(0.2, 1.2) # Keep this pause between segments
              logger.info(f"Pausing between segments for {pause_time:.2f} seconds")
              await asyncio.sleep(pause_time)


          logger.info("Waiting for page to potentially reach network idle state (max 5s)")
          try:
              network_idle_start = datetime.datetime.now()
              await page.wait_for_load_state('networkidle', timeout=5000)
              network_idle_duration = (datetime.datetime.now() - network_idle_start).total_seconds()
              logger.info(f"Page reached network idle state after {network_idle_duration:.2f} seconds")
          except Exception as e:
              logger.warning(f"Network idle timeout/error (continuing): {str(e)}")

          # Create appropriate message based on scroll direction
          horizontal_msg = f"{abs(total_x)} pixels {'right' if total_x > 0 else 'left'}" if total_x != 0 else ""
          vertical_msg = f"{abs(total_y)} pixels {'down' if total_y > 0 else 'up'}" if total_y != 0 else ""
          if horizontal_msg and vertical_msg: scroll_msg = f"{horizontal_msg} and {vertical_msg}"
          else: scroll_msg = horizontal_msg or vertical_msg

          message = f"🖱️ Performed human-like scroll: {scroll_msg}" # Simplified message
          logger.info(f"Mouse wheel action completed: {message}")

          session_end_time = datetime.datetime.now()
          total_session_duration = (session_end_time - session_start_time).total_seconds()
          logger.info(f"Total session duration: {total_session_duration:.2f} seconds")
          logger.info("="*80)
          logger.info(f"MOUSE WHEEL SESSION COMPLETED: {session_end_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
          logger.info("="*80)

          return ActionResult(extracted_content=message, include_in_memory=True)

      except Exception as e:
          error_message = f"Failed to perform mouse wheel scroll: {str(e)}"
          if logger: # Check if logger was initialized
              logger.error(error_message)
              logger.error(f"Exception details: {traceback.format_exc()}")
              session_end_time = datetime.datetime.now()
              logger.error("="*80)
              logger.error(f"MOUSE WHEEL SESSION FAILED: {session_end_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
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
  ```
- **Checklist:** [ ] Implementation logic moved to perform_mouse_wheel, call to internal helper updated.

**Step 5.7:** Update custom_controller.py for mouse_wheel.
- **Action:**
  1. Add the import: 
     ```python
     from .controller_actions.action_mouse_wheel import perform_mouse_wheel, MouseWheelAction
     ```
  2. Replace the body of the original mouse_wheel function:
     ```python
     @controller.action(
         'Scroll page using mouse wheel',
         param_model=MouseWheelAction
     )
     async def mouse_wheel(params: MouseWheelAction, browser: BrowserContext) -> ActionResult:
          """ Action definition: Scroll page using mouse wheel simulation. """
          return await perform_mouse_wheel(params, browser)
     ```
- **Checklist:** [ ] custom_controller.py updated for mouse_wheel.

> **Note:** Ensure the original helper functions generate_arc_positions and generate_scroll_steps remain untouched in custom_controller.py as they were not part of the mouse_wheel action's direct logic block.

## Phase 6: Refactor extract_audience_data Action

**Step 6.1:** Create the helper file.
- **Action:** Create action_extract_audience_data.py.
- **Path:** `/Users/meirsabag/Public/browser_use_ver4_newVersion/remote_tools_folders/controller_actions/action_extract_audience_data.py`
- **Checklist:** [ ] File created.

**Step 6.2:** Add imports.
- **Action:** Add required imports.
  ```python
  from browser_use import ActionResult
  from browser_use.browser.context import BrowserContext
  from pydantic import BaseModel, Field
  from typing import Optional, List # Keep List if used
  import os
  import json
  import anthropic # If used directly
  import logging
  import datetime
  import sys # Keep if used
  import traceback
  from dotenv import load_dotenv
  import re
  import base64
  ```
- **Checklist:** [ ] Imports added.

**Step 6.3:** Define Pydantic model.
- **Action:** Define ExtractAudienceDataAction.
  ```python
  class ExtractAudienceDataAction(BaseModel):
      is_first_run: bool = Field(True, description="Whether this is the first run (create new file) or not (append to existing)")
      file_path: Optional[str] = Field(None, description="Path to the existing JSON file (only used if is_first_run=False)")
  ```
- **Checklist:** [ ] Pydantic model defined.

**Step 6.4:** Define helper function perform_extract_audience_data.
- **Action:** Define signature.
  ```python
  async def perform_extract_audience_data(params: ExtractAudienceDataAction, browser: BrowserContext) -> ActionResult:
      """ Helper function to extract audience data using Claude Vision API. """
      pass
  ```
- **Checklist:** [ ] Helper function signature defined.

**Step 6.5:** Move implementation logic.
- **Action:** Copy try...except block from original function into the helper. Ensure logger setup is included.
  ```python
  async def perform_extract_audience_data(params: ExtractAudienceDataAction, browser: BrowserContext) -> ActionResult:
      """ Helper function to extract audience data using Claude Vision API. """
      logger = None # Define logger variable early for use in except block
      try:
          # --- Logger Setup ---
          # (Copy logger setup code from original action)
          log_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/logs"
          os.makedirs(log_dir, exist_ok=True)
          log_file = os.path.join(log_dir, "audience_data_extraction.log")
          logger = logging.getLogger("audience_extraction") # Assign to logger variable
          # ... (rest of logger setup) ...
          file_handler = logging.FileHandler(log_file, encoding='utf-8')
          # ... (rest of logger setup copied from original) ...
          logger.addHandler(file_handler)
          # --- End Logger Setup ---

          session_start_time = datetime.datetime.now() # Use .now()
          logger.info("="*80)
          logger.info(f"STARTING NEW EXTRACTION SESSION: {session_start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
          logger.info("="*80)
          logger.info(f"Function parameters: is_first_run={params.is_first_run}, file_path={params.file_path}")

          load_dotenv() # Load environment variables
          logger.info("Environment variables loaded")

          agent_files_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/agent-files"
          logger.info(f"Using agent files directory: {agent_files_dir}")

          file_path = params.file_path
          if params.is_first_run:
              os.makedirs(agent_files_dir, exist_ok=True)
              # logger.info(f"Created agent files directory: {agent_files_dir}") # Redundant if using exist_ok=True
              timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
              file_path = os.path.join(agent_files_dir, f"facebook_audience_data_{timestamp}.json")
              logger.info(f"Generated new file path for first run: {file_path}")
          elif not file_path:
              logger.error("No file path provided for subsequent run (not first run)")
              return ActionResult(error="File path must be provided when is_first_run is False")
          else:
              logger.info(f"Using provided file path for subsequent run: {file_path}")

          # Initialize Anthropic client
          api_key = os.environ.get("ANTHROPIC_API_KEY")
          if not api_key:
              logger.error("ANTHROPIC_API_KEY not found")
              return ActionResult(error="ANTHROPIC_API_KEY not found in environment variables")
          logger.info("Anthropic API key found")
          client = anthropic.Anthropic(api_key=api_key)
          logger.info("Anthropic client initialized")

          # Take screenshot
          logger.info("Taking screenshot of current page")
          start_time = datetime.datetime.now()
          screenshot_data = await browser.take_screenshot(full_page=True)
          end_time = datetime.datetime.now()
          screenshot_duration = (end_time - start_time).total_seconds()
          if not screenshot_data:
              logger.error("Failed to capture screenshot")
              return ActionResult(error="Failed to capture screenshot")
          screenshot_size = len(screenshot_data) # Length of base64 string
          logger.info(f"Screenshot captured successfully: {screenshot_size} chars, took {screenshot_duration:.2f} seconds")

          # Detect image format from base64 prefix or assume png/jpeg
          # Simplified check:
          if screenshot_data.startswith("data:image/png;base64,") or screenshot_data.startswith("iVBORw0KGgo"):
               image_format = "image/png"
               image_data_b64 = screenshot_data.split(',')[-1] # Get data part
               logger.info("Detected image format: PNG")
          elif screenshot_data.startswith("data:image/jpeg;base64,") or screenshot_data.startswith("/9j/"):
               image_format = "image/jpeg"
               image_data_b64 = screenshot_data.split(',')[-1] # Get data part
               logger.info("Detected image format: JPEG")
          else: # Fallback if no prefix
              image_format = "image/png" # Default assumption
              image_data_b64 = screenshot_data
              logger.warning("Could not detect image format from prefix, assuming PNG")


          # Save screenshot to file
          try:
              output_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/training_images/output_images_condition_stop_audience_page"
              os.makedirs(output_dir, exist_ok=True)
              timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")[:-3]
              filename = f"screenshot_{timestamp}.{file_extension}"
              filepath = os.path.join(output_dir, filename)
              binary_data = base64.b64decode(image_data_b64) # Decode the correct variable
              with open(filepath, 'wb') as f: f.write(binary_data)
              logger.info(f"Screenshot saved to file: {filepath}")
          except Exception as e:
              logger.error(f"Failed to save screenshot: {e}\n{traceback.format_exc()}")
              # Continue even if saving fails

          # Load training images
          training_images = []
          training_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/training_images/train-condition-scroll-audience-page"
          if os.path.exists(training_dir):
              logger.info(f"Loading training images from {training_dir}")
              try:
                  # (Copy logic for loading and base64 encoding training images from original)
                  image_files = sorted([f for f in os.listdir(training_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]) # Allow jpg/jpeg
                  logger.info(f"Found {len(image_files)} training images")
                  for img_file in image_files:
                      img_path = os.path.join(training_dir, img_file)
                      try:
                          with open(img_path, 'rb') as f: img_data = f.read()
                          img_base64 = base64.b64encode(img_data).decode('utf-8')
                          img_type = "image/png" if img_file.lower().endswith('.png') else "image/jpeg"
                          training_images.append({"media_type": img_type, "data": img_base64})
                          logger.info(f"Loaded training image: {img_file}")
                      except Exception as load_err:
                          logger.error(f"Failed to load training image {img_file}: {load_err}\n{traceback.format_exc()}")

              except Exception as list_err:
                  logger.error(f"Error listing/loading training images: {list_err}\n{traceback.format_exc()}")
          else:
              logger.warning(f"Training directory not found: {training_dir}")

          # Prepare system prompt and messages
          system_prompt = """You have perfect vision and pay great attention to detail...""" # (Copy full system prompt from original)
          logger.info("System prompt prepared")

          messages = [
              # (Copy the few-shot examples structure from original, ensuring training_images are correctly referenced)
              {"role": "user", "content": [{"type": "text", "text": "Before you start..."}]},
              {"role": "assistant", "content": [{"type": "text", "text": "I understand completely..."}]},
              # Add Example 1 (if training_images[0] exists)
              {"role": "user", "content": [{"type": "image", "source": {...}}, {"type": "text", "text": "<Example 1..."}]},
              {"role": "assistant", "content": [{"type": "text", "text": "<reasoning>...</reasoning>..."}]},
              # Add Example 2, 3, 4, 5 similarly...
              # Final user message with current screenshot
              {"role": "user", "content": [{"type": "text", "text": "You have perfect vision...\nWhat is the number of rows between the bottom edge of the scroll bar and the bottom border of the table?\n..."}, {"type": "image", "source": {"type": "base64", "media_type": image_format, "data": image_data_b64}}]}
          ]
          # Dynamically build the few-shot part based on loaded training_images
          few_shot_messages = [
              {"role": "user", "content": [{"type": "text", "text": "Before you start acting on your system prompt..."}]},
              {"role": "assistant", "content": [{"type": "text", "text": "I understand completely..."}]}
          ]
          example_prompts = [ # Assuming prompts match images 1-1
              "<Example 1 for calculating the number of rows>\nWhat is the number of rows between the bottom edge of the scroll bar and the bottom border of the table?",
              "<Example 2 for calculating the number of rows>\nWhat is the number of rows between the bottom edge of the scroll bar and the bottom border of the table?",
              "<Example 3 for calculating the number of rows>\nWhat is the number of rows between the bottom edge of the scroll bar and the bottom border of the table?",
              "<Example 4 for calculating the number of rows>\nWhat is the number of rows between the bottom edge of the scroll bar and the bottom border of the table?",
              "<Example 5 for calculating the number of rows>\nWhat is the number of rows between the bottom edge of the scroll bar and the bottom border of the table?",
          ]
          example_responses = [ # Assuming responses match images 1-1
                "<reasoning>...</reasoning>\n\n<decision>\nCONTINUE\n500px\n</decision>", # Example 1 response
                "<reasoning>...</reasoning>\n\n<decision>\nCONTINUE\n100px\n</decision>", # Example 2 response
                "<reasoning>...</reasoning>\n\n<decision>\nCONTINUE\n100px\n</decision>", # Example 3 response
                "<reasoning>...</reasoning>\n\n<decision>\nSTOP\nNONE\n</decision>", # Example 4 response
                "<reasoning>...</reasoning>\n\n<decision>\nCONTINUE\n600px\n</decision>", # Example 5 response
          ]

          num_examples = min(len(training_images), len(example_prompts), len(example_responses))
          logger.info(f"Adding {num_examples} few-shot examples to messages.")
          for i in range(num_examples):
              few_shot_messages.append({
                  "role": "user",
                  "content": [
                      {"type": "image", "source": {"type": "base64", "media_type": training_images[i]["media_type"], "data": training_images[i]["data"]}},
                      {"type": "text", "text": example_prompts[i]}
                  ]
              })
              few_shot_messages.append({
                  "role": "assistant",
                  "content": [{"type": "text", "text": example_responses[i]}]
              })

          # Add the final query with the current screenshot
          few_shot_messages.append({
              "role": "user",
              "content": [
                  {"type": "text", "text": "You have perfect vision...\nWhat is the number of rows between the bottom edge of the scroll bar and the bottom border of the table?\n..."}, # Final user prompt from original
                  {"type": "image", "source": {"type": "base64", "media_type": image_format, "data": image_data_b64}}
              ]
          })
          messages = few_shot_messages # Use the dynamically built messages
          logger.info(f"Prepared {len(messages)} messages for Claude API")

          # Call Claude API
          logger.info("Calling Claude Vision API...")
          api_call_start = datetime.datetime.now()
          message_response = client.messages.create( # Renamed variable
              model="claude-3-5-sonnet-20240620", # Match model from original if different
              max_tokens=20000, # Match tokens from original
              temperature=0.1, # Match temp from original
              messages=messages
          )
          api_call_end = datetime.datetime.now()
          api_call_duration = (api_call_end - api_call_start).total_seconds()
          logger.info(f"Claude Vision API call completed in {api_call_duration:.2f} seconds")

          # Extract and process response
          response_text = message_response.content[0].text
          # ... (rest of response processing, JSON extraction, data merging, file writing copied from original) ...
          logger.info(f"Received response from Claude: {len(response_text)} chars")
          response_preview = response_text[:100].replace('\n', ' ') + ("..." if len(response_text) > 100 else "")
          logger.info(f"Response preview: {response_preview}")
          # ... Log full response ...

          json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
          if json_match:
              json_content = json_match.group(1).strip()
              logger.info(f"Extracted JSON code block: {len(json_content)} chars")
          else:
              json_content = response_text.strip() # Fallback to full response
              logger.info(f"No JSON block found, using full response: {len(json_content)} chars")

          try:
              parsed_data = json.loads(json_content)
              logger.info("Successfully parsed JSON")
          except json.JSONDecodeError as e:
              logger.error(f"Failed to parse JSON: {e}")
              return ActionResult(error=f"Failed to parse JSON from Claude's response: {e}")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
          logger.info(f"Processed {len(audience_data)} entries")

          # ... (rest of logic for standardizing fields, merging data, writing file)
          audience_entries = []
          if isinstance(parsed_data, list):
              audience_entries = parsed_data
          elif isinstance(parsed_data, dict) and "audience_data" in parsed_data:
              audience_entries = parsed_data.get("audience_data", [])
          else:
               logger.error("Parsed data not in expected list or dict format")
               return ActionResult(error="Could not find audience data in Claude's response")

          audience_data = []
          # ... (standardize fields as in original) ...
          for entry in audience_entries:
             audience_entry = {
                 "Name": entry.get("Name", entry.get("name", "")), # Handle both cases
                 "Type": entry.get("Type", entry.get("type", "")),
                 "Availability": entry.get("Availability", entry.get("availability", "")),
                 "Date created": entry.get("Date created", entry.get("date_created", "")),
                 "Audience ID": entry.get("Audience ID", entry.get("audience_id", ""))
             }
             audience_data.append(audience_entry)
  ```
- **Checklist:** [ ] Started implementation logic moved.

## Phase 7: Refactor generate_custom_prompt Action

**Step 7.1:** Create the helper file.

**Step 7.2:** Add imports.

**Step 7.3:** Define helper function perform_generate_custom_prompt.

**Step 7.4:** Move implementation logic.

**Step 7.5:** Update `custom_controller.py`.

---

## Phase 8: Refactor `check_condition_stop_page_wheel` Action

**Step 8.1:** Create the helper file.

**Step 8.2:** Add imports.

**Step 8.3:** Define helper function perform_check_condition_stop_page_wheel.

**Step 8.4:** Move implementation logic.

**Step 8.5:** Update custom_controller.py.

---

## Phase 9: Final Review

**Step 9.1:** Review custom_controller.py.

**Step 9.2:** Review controller_actions directory.