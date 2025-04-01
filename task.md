# Refactoring Plan: Modularizing `custom_controller.py`

## Overview

**Goal:** Refactor `custom_controller.py` to improve modularity by separating action logic and helper functions into a dedicated directory structure, while preserving existing functionality.

## Phase 1: Setup and Helper Function Migration

### 1. Create Directory Structure
- Create a new directory named `controller_logic` inside the `remote_tools_folders` directory.
- **Path:** `remote_tools_folders/controller_logic/`

### 2. Create Package Initializer
- Create an empty file named `__init__.py` inside the new directory.
- **Path:** `remote_tools_folders/controller_logic/__init__.py`
- **Purpose:** This makes `controller_logic` a Python package, allowing relative imports.

### 3. Create Utility File
- Create a new file named `utils.py` inside the `controller_logic` directory.
- **Path:** `remote_tools_folders/controller_logic/utils.py`

### 4. Migrate Helper Functions
- **Cut** the following function definitions from `custom_controller.py` and **paste** them into `remote_tools_folders/controller_logic/utils.py`:
  - `generate_arc_positions`
  - `create_segments`
  - `generate_speed_profile`
  - `get_speed_factor`
  - `generate_scroll_steps`
  - `scroll_segment_with_1px_increments` (move here for potential broader reuse)
- Add necessary imports to the top of `utils.py`:
  ```python
  import math
  import random
  from typing import Optional, List, Tuple
  import asyncio
  ```

## Phase 2: Action Logic Migration

*For each action, we will create a logic file, move the core implementation, and define an exported function.*

### 5. Create `mouse_wheel_logic.py`
- Create file: `remote_tools_folders/controller_logic/mouse_wheel_logic.py`
- Define function: 
  ```python
  async def execute_mouse_wheel(params, page, logger)
  ```
- Copy the entire `try` block content from the `mouse_wheel` function in `custom_controller.py` into `execute_mouse_wheel`.
- Copy the *nested function definition* `scroll_segment_with_logging` into `mouse_wheel_logic.py` (likely *outside* `execute_mouse_wheel` but within the same file).
- Ensure all necessary imports are added.
- Modify `execute_mouse_wheel` to `return` the final success message string instead of `ActionResult`.
- Modify `execute_mouse_wheel` to `raise` exceptions if they occur, allowing the original `mouse_wheel` function to catch them.

### 6. Create `extract_audience_logic.py`
- Create file: `remote_tools_folders/controller_logic/extract_audience_logic.py`
- Define function: 
  ```python
  async def execute_extract_audience(params, browser, logger)
  ```
- Copy the entire `try` block content from the `extract_audience_data` function in `custom_controller.py` into `execute_extract_audience`.
- Ensure all necessary imports are added.
- Modify `execute_extract_audience` to return a tuple: `(message, metadata)` where `message` is the success string and `metadata` is the dictionary.
- Modify `execute_extract_audience` to `raise` exceptions.

### 7. Create `check_condition_logic.py`
- Create file: `remote_tools_folders/controller_logic/check_condition_logic.py`
- Define function: 
  ```python
  async def execute_check_condition(browser, logger)
  ```
- Copy the entire `try` block content from the `check_condition_stop_page_wheel` function in `custom_controller.py` into `execute_check_condition`.
- Ensure all necessary imports are added.
- Modify `execute_check_condition` to return a tuple `(message, metadata)`.
- Modify `execute_check_condition` to `raise` exceptions.

### 8. Create `mouse_actions_logic.py`
- Create file: `remote_tools_folders/controller_logic/mouse_actions_logic.py`
- Define three functions for the mouse action logic:
  ```python
  async def execute_move_mouse(params, page)
  async def execute_mouse_click(page)
  async def execute_mouse_hover(x, y, page)
  ```
- Copy the respective `try` block content from each original function.
- Return success message strings and raise exceptions.
- Add necessary imports.

### 9. Create `custom_prompt_logic.py`
- Create file: `remote_tools_folders/controller_logic/custom_prompt_logic.py`
- Define:
  ```python
  async def execute_generate_custom_prompt()
  ```
- Copy `try` block content from `generate_custom_prompt`.
- Return the prompt string and the metadata dict: `(prompt, metadata)`.
- Raise exceptions.
- Add necessary imports.

## Phase 3: Update `custom_controller.py`

### 10. Remove Migrated Code
- Delete the helper function definitions (`generate_arc_positions`, etc.) that were moved in Step 4.
- Delete the *content* inside the `try` blocks of the action functions that was moved in Steps 5-9.
- Keep the function definitions, decorators, parameters, and the `try...except ActionResult(error=...)` structure.

### 11. Add Imports for Logic
- At the top of `custom_controller.py`, add relative imports for the new logic functions:
  ```python
  from .controller_logic.utils import generate_arc_positions # Example if needed directly
  from .controller_logic.mouse_actions_logic import execute_move_mouse, execute_mouse_click, execute_mouse_hover
  from .controller_logic.mouse_wheel_logic import execute_mouse_wheel
  from .controller_logic.extract_audience_logic import execute_extract_audience
  from .controller_logic.check_condition_logic import execute_check_condition
  from .controller_logic.custom_prompt_logic import execute_generate_custom_prompt
  # Add other imports from utils if they are directly needed by controller actions
  ```

### 12. Update `move_mouse` Action
- Inside the `try` block:
  ```python
  page = await browser.get_current_page()
  message = await execute_move_mouse(params, page)
  return ActionResult(extracted_content=message, include_in_memory=True)
  ```

### 13. Update `mouse_click` Action
- Inside the `try` block:
  ```python
  page = await browser.get_current_page()
  message = await execute_mouse_click(page)
  return ActionResult(extracted_content=message, include_in_memory=True)
  ```

### 14. Update `mouse_hover` Action
- Inside the `try` block:
  ```python
  page = await browser.get_current_page()
  message = await execute_mouse_hover(x, y, page) # Pass x, y if they are params
  return ActionResult(extracted_content=message, include_in_memory=True)
  ```

### 15. Update `mouse_wheel` Action
- Inside the `try` block:
  ```python
  # Logger setup might remain here or be initialized/passed differently
  log_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/logs"
  # ... (rest of logger setup) ...
  logger = logging.getLogger("mouse_wheel") 
  # ... (ensure logger is configured) ...

  page = await browser.get_current_page()
  message = await execute_mouse_wheel(params, page, logger) # Pass logger
  
  return ActionResult(extracted_content=message, include_in_memory=True)
  ```
- Adjust the `except` block if the logic function handles logging internally.

### 16. Update `extract_audience_data` Action
- Inside the `try` block:
  ```python
  # Logger setup
  log_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/logs"
  # ... (rest of logger setup) ...
  logger = logging.getLogger("audience_extraction")
  # ... (ensure logger is configured) ...

  message, metadata = await execute_extract_audience(params, browser, logger) # Pass logger
  return ActionResult(extracted_content=message, include_in_memory=True, metadata=metadata)
  ```

### 17. Update `check_condition_stop_page_wheel` Action
- Inside the `try` block:
  ```python
  # Logger setup
  log_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/logs"
  # ... (rest of logger setup) ...
  logger = logging.getLogger("scroll_condition_check")
  # ... (ensure logger is configured) ...

  message, metadata = await execute_check_condition(browser, logger) # Pass logger
  return ActionResult(extracted_content=message, include_in_memory=True, metadata=metadata)
  ```

### 18. Update `generate_custom_prompt` Action
- Inside the `try` block:
  ```python
  prompt, metadata = await execute_generate_custom_prompt()
  return ActionResult(extracted_content=prompt, include_in_memory=True, metadata=metadata)
  ```

### 19. Review and Test
- Carefully review all changes in `custom_controller.py` and the new files in `controller_logic/`.
- Check for any missing imports in the new files.
- Ensure relative imports in `custom_controller.py` are correct.
- Thoroughly test all actions defined in `custom_controller.py` to confirm they still work exactly as before the refactoring.

## Why This Approach Won't Break Existing Code

- We are **moving** existing, working code blocks, not rewriting their internal logic.
- The `@controller.action` decorators, function signatures, Pydantic models, and the overall structure of how actions are called and results are handled remain unchanged in `custom_controller.py`.
- The `try...except` blocks are preserved in `custom_controller.py`, ensuring that errors raised from the logic functions are caught and returned as `ActionResult(error=...)` just like before.
- Dependencies (like `browser`, `params`, `page`, `logger`) are explicitly passed to the logic functions.

This refactoring separates the concerns, making `custom_controller.py` primarily responsible for action registration and interfacing with the `browser-use` framework, while the detailed implementation logic resides in the `controller_logic` package.
