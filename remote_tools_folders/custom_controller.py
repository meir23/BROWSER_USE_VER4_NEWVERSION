"""
Custom controller for Browser-Use with mouse positioning functionality.
"""

from browser_use import Controller, ActionResult
from browser_use.browser.context import BrowserContext
from pydantic import BaseModel, Field
from typing import Optional, List, Tuple
import random
import math
import asyncio
import base64
import datetime
import os
import logging
import traceback

# Function to generate arc-based mouse movement positions
def generate_arc_positions(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    steps: int = 20,
    arc_height_factor: float = 0.2
) -> list:
    """
    Generate a list of positions along a parabolic arc between two points.
    
    Args:
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        end_x: Ending X coordinate
        end_y: Ending Y coordinate
        steps: Number of intermediate steps (default: 20)
        arc_height_factor: Controls the height of the arc as a proportion of distance (default: 0.2)
        
    Returns:
        List of (x, y) coordinate tuples along the arc
    """
    # Calculate deltas and distance
    dx = end_x - start_x
    dy = end_y - start_y
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Compute arc height based on distance
    arc_height = distance * arc_height_factor
    
    # Create empty list to store positions
    positions = []
    
    # Iterate over steps + 1 increments (to include the end point)
    for i in range(steps + 1):
        # Calculate progress along the path (0.0 to 1.0)
        t = i / steps
        
        # Linear interpolation of x and y
        x = start_x + dx * t
        y = start_y + dy * t
        
        # Apply parabolic vertical offset
        # Formula: -4 * (t - 0.5)² + 1 creates a parabola with peak at t=0.5
        parabola = -4 * (t - 0.5)**2 + 1
        y_offset = parabola * arc_height
        
        # Add small random noise to make movement more human-like
        y = y - y_offset + random.uniform(-1, 1)
        x = x + random.uniform(-1, 1)  # Small x-axis noise as well
        
        # Add the position to our list
        positions.append((x, y))
    
    return positions

# Helper function to create segments for 1px increment scrolling
def create_segments(total_distance: int) -> List[int]:
    """
    Break total scroll distance into natural segments.
    
    Args:
        total_distance: Total distance to scroll (positive or negative)
        
    Returns:
        List of segment distances that sum to total_distance
    """
    if abs(total_distance) <= 5:
        return [total_distance]  # For tiny scrolls, just one segment
        
    # Number of segments depends on total distance
    segment_count = max(3, min(8, abs(total_distance) // 100))
    
    # Create segments with natural size distribution
    # (Middle segments typically larger than start/end)
    segments = []
    remaining = total_distance
    
    for i in range(segment_count):
        # Last segment takes remaining distance
        if i == segment_count - 1:
            segments.append(remaining)
            break
            
        # Otherwise create variable segment sizes
        # Use bell curve distribution (middle segments larger)
        position = i / (segment_count - 1)
        weight = math.sin(position * math.pi)  # 0 → 1 → 0 distribution
        
        # Add randomness
        weight *= random.uniform(0.8, 1.2)
        
        # Calculate segment size (ensure at least 1px)
        segment_size = int(max(1, (total_distance * weight) / (segment_count - 0.5)))
        
        # Ensure we don't overshoot
        segment_size = min(segment_size, remaining)
        segments.append(segment_size)
        remaining -= segment_size
        
    return segments

# Generate speed profile for natural scrolling
def generate_speed_profile(duration_seconds: float) -> List[float]:
    """
    Generate a speed profile for natural scrolling acceleration/deceleration.
    
    Args:
        duration_seconds: Duration of the scrolling segment in seconds
        
    Returns:
        List of speed factors for different time positions (0.0 to 1.0)
    """
    # Create time positions (0.0 to 1.0)
    steps = 100
    time_positions = [i/steps for i in range(steps+1)]
    
    # Different humans have different scrolling patterns
    # Randomly choose between acceleration profiles:
    profile_type = random.choice([
        "quick_start_slow_end",    # 40% probability
        "gradual_accel_decel",     # 40% probability
        "constant_with_bursts",    # 20% probability
    ])
    
    speed_factors = []
    
    for t in time_positions:
        if profile_type == "quick_start_slow_end":
            # Fast acceleration, longer deceleration
            if t < 0.2:
                # Quick ramp up
                factor = 0.4 + (t / 0.2) * 0.6
            elif t > 0.7:
                # Gradual slow down
                factor = 1.0 - ((t - 0.7) / 0.3) * 0.6
            else:
                # Sustained speed in middle
                factor = 1.0
                
        elif profile_type == "gradual_accel_decel":
            # Sinusoidal acceleration/deceleration (smoother)
            factor = math.sin((t * math.pi) + math.pi/2) * 0.5 + 0.5
            
        else:  # "constant_with_bursts"
            # Mostly constant speed with occasional speed bursts
            factor = 0.7  # Base speed
            
            # Add random bursts
            for burst_center in [0.3, 0.6, 0.8]:
                # If close to a burst center
                distance = abs(t - burst_center)
                if distance < 0.1:
                    # Add boost based on proximity to burst center
                    burst_factor = 0.3 * (1 - (distance / 0.1))
                    factor += burst_factor
        
        # Add small random noise to the factor
        factor *= random.uniform(0.95, 1.05)
        
        # Ensure factor is positive and reasonable
        factor = max(0.3, min(1.2, factor))
        speed_factors.append(factor)
    
    return speed_factors

# Helper function to get speed factor at a specific time position
def get_speed_factor(speed_profile: List[float], time_position: float) -> float:
    """
    Get the speed factor for the current time position.
    
    Args:
        speed_profile: List of speed factors
        time_position: Current time position (0.0 to 1.0)
        
    Returns:
        Speed factor at the given time position
    """
    index = int(time_position * len(speed_profile))
    return speed_profile[min(index, len(speed_profile)-1)]

# 1px-increment scrolling function
async def scroll_segment_with_1px_increments(page, segment_x: int, segment_y: int) -> None:
    """
    Scroll a segment using only 1px increments with variable timing
    that exactly matches real human scrolling patterns.
    
    Args:
        page: Playwright page object
        segment_x: Horizontal pixels to scroll in this segment
        segment_y: Vertical pixels to scroll in this segment
    """
    # Calculate total pixels to scroll (Manhattan distance)
    total_pixels = abs(segment_x) + abs(segment_y)
    if total_pixels == 0:
        return
        
    # Determine direction for each axis
    x_dir = 1 if segment_x > 0 else -1 if segment_x < 0 else 0
    y_dir = 1 if segment_y > 0 else -1 if segment_y < 0 else 0
    
    # Count remaining pixels for each axis
    x_remaining = abs(segment_x)
    y_remaining = abs(segment_y)
    
    # Initial delay based on real human behavior (2000-2600ms)
    # Only for the first segment
    if random.random() < 0.7:  # 70% chance of initial pause
        initial_delay = random.uniform(2.0, 2.6)  # 2000-2600ms
        await asyncio.sleep(initial_delay)
    
    # Begin scrolling
    step_counter = 0
    steps_since_last_pause = 0
    
    # Track scroll clusters for realistic timing
    current_cluster_size = random.randint(10, 20)  # Scrolls before rhythm change
    cluster_count = 0
    
    # Use real human delay patterns: 15-18ms base
    while x_remaining > 0 or y_remaining > 0:
        step_counter += 1
        steps_since_last_pause += 1
        cluster_count += 1
        
        # Decide which axis to move next (probabilistic)
        move_x = False
        move_y = False
        
        if x_remaining > 0 and y_remaining > 0:
            # If both axes have remaining distance, choose probabilistically
            x_prob = x_remaining / (x_remaining + y_remaining)
            move_x = random.random() < x_prob
            move_y = not move_x
        elif x_remaining > 0:
            move_x = True
        elif y_remaining > 0:
            move_y = True
            
        # Perform the 1px scroll
        wheel_x = x_dir if move_x else 0
        wheel_y = y_dir if move_y else 0
        
        # Occasional micro-tremor (hand instability)
        tremor_chance = 0.02  # 2% chance
        if random.random() < tremor_chance:
            if move_x and random.random() < 0.5:
                wheel_x = 0  # Skip a pixel occasionally
            if move_y and random.random() < 0.5:
                wheel_y = 0  # Skip a pixel occasionally
                
        # Send the wheel event
        await page.mouse.wheel(wheel_x, wheel_y)
        
        # Update remaining distances
        if move_x:
            x_remaining -= 1
        if move_y:
            y_remaining -= 1
            
        # TIMING PATTERNS BASED ON REAL HUMAN DATA
        
        # 1. Base delay: 15-18ms (most common in real data)
        wait_time = random.uniform(0.015, 0.018)  # 15-18ms
        
        # 2. Micro-burst chance (7-9ms delay) - observed in real data
        if random.random() < 0.08:  # 8% chance
            wait_time = random.uniform(0.007, 0.009)  # 7-9ms
        
        # 3. Medium pause (24-33ms) - every ~15-25 scrolls
        if steps_since_last_pause > random.randint(15, 25) and random.random() < 0.3:
            wait_time = random.uniform(0.024, 0.033)  # 24-33ms
            steps_since_last_pause = 0
        
        # 4. Longer pause patterns based on real data
        # These were observed to occur every ~30-40 scroll actions
        if step_counter % random.randint(30, 40) == 0:
            pause_type = random.choices(
                ["medium", "long", "very_long", "cognitive"],
                weights=[0.4, 0.3, 0.2, 0.1],
                k=1
            )[0]
            
            if pause_type == "medium":
                wait_time = random.uniform(0.065, 0.085)  # ~80ms
            elif pause_type == "long":
                wait_time = random.uniform(0.09, 0.12)  # ~100ms
            elif pause_type == "very_long":
                wait_time = random.uniform(0.13, 0.16)  # ~150ms
            else:  # cognitive
                wait_time = random.uniform(0.35, 0.45)  # ~400ms
        
        # 5. Cluster boundary - when we need to change our rhythm
        if cluster_count >= current_cluster_size:
            # Create a more noticeable pause between clusters
            wait_time = random.uniform(0.08, 0.11)  # 80-110ms
            current_cluster_size = random.randint(10, 20)  # New cluster size
            cluster_count = 0
        
        # Apply the wait time
        await asyncio.sleep(wait_time)

# Helper function to split total scroll distance into variable-sized steps
def generate_scroll_steps(total_distance: float, steps_count: int) -> list:
    """
    Generate a list of scroll step sizes that sum approximately to the total distance.
    Creates variable-sized steps that mimic natural human scrolling behavior with
    acceleration and deceleration patterns.
    
    Args:
        total_distance: Total distance to scroll
        steps_count: Number of steps to divide the scroll into
        
    Returns:
        List of scroll distances for each step
    """
    if total_distance == 0:
        return [0] * steps_count
    
    # Create acceleration/deceleration profile (slow start, faster middle, slow end)
    # This better mimics how humans naturally scroll
    positions = [i/(steps_count-1) if steps_count > 1 else 0.5 for i in range(steps_count)]
    weights = []
    
    for pos in positions:
        # Sinusoidal acceleration profile (slow→fast→slow)
        # sin(π·x) creates a bell curve from 0 to 1
        weight = math.sin(pos * math.pi)
        
        # Add slight randomness to make it more natural
        weight *= random.uniform(0.9, 1.1)
        weights.append(weight)
    
    # Ensure we have positive values
    total_weight = sum(weights)
    
    # Calculate step sizes based on the acceleration profile weights
    steps = [int(total_distance * weight / total_weight) for weight in weights]
    
    # Adjust the last step to ensure the sum is exactly the total distance
    steps[-1] = total_distance - sum(steps[:-1])
    
    return steps

# Create a model for the mouse movement parameters
class MouseMoveAction(BaseModel):
    x: float = Field(..., description="X coordinate relative to the viewport in CSS pixels")
    y: float = Field(..., description="Y coordinate relative to the viewport in CSS pixels")
    steps: Optional[int] = Field(1, description="Number of intermediate steps for the movement (default: 1)")

# Create a model for the mouse wheel parameters
class MouseWheelAction(BaseModel):
    delta_x: float = Field(0, description="Pixels to scroll horizontally (positive for right, negative for left). For most websites, use 0 for vertical-only scrolling.")
    delta_y: float = Field(..., description="Pixels to scroll vertically (positive for down, negative for up). Typical values: 100-300 for small scrolls, 500-800 for larger scrolls.")

# Create a model for the Facebook audience extraction parameters
class ExtractAudienceDataAction(BaseModel):
    is_first_run: bool = Field(True, description="Whether this is the first run (create new file) or not (append to existing)")
    file_path: Optional[str] = Field(None, description="Path to the existing JSON file (only used if is_first_run=False)")

# Initialize the controller
controller = Controller()

@controller.action(
    'Move mouse cursor to specific coordinates on the page',
    param_model=MouseMoveAction
)
async def move_mouse(params: MouseMoveAction, browser: BrowserContext) -> ActionResult:
    """
    Move the mouse cursor to specific coordinates on the page.
    
    Args:
        params: MouseMoveAction with x, y coordinates and optional steps
        browser: Browser context instance
    
    Returns:
        ActionResult: Result of the action with confirmation message
    """
    try:
        page = await browser.get_current_page()
        await page.mouse.move(params.x, params.y, steps=params.steps)
        message = f"🖱️ Mouse moved to coordinates ({params.x}, {params.y})"
        return ActionResult(extracted_content=message, include_in_memory=True)
    except Exception as e:
        error_message = f"Failed to move mouse: {str(e)}"
        return ActionResult(error=error_message)

# Optional - add more mouse-related functions if needed

@controller.action('Click mouse at current position')
async def mouse_click(browser: BrowserContext) -> ActionResult:
    """
    Click the mouse at its current position.
    
    Args:
        browser: Browser context instance
    
    Returns:
        ActionResult: Result of the action with confirmation message
    """
    try:
        page = await browser.get_current_page()
        await page.mouse.click(0, 0, position_relative_to_element=False)
        message = "🖱️ Mouse clicked at current position"
        return ActionResult(extracted_content=message, include_in_memory=True)
    except Exception as e:
        error_message = f"Failed to click mouse: {str(e)}"
        return ActionResult(error=error_message)

@controller.action('Perform mouse hover at specific coordinates')
async def mouse_hover(x: float, y: float, browser: BrowserContext) -> ActionResult:
    """
    Move the mouse to specified coordinates to perform a hover action.
    
    Args:
        x: X coordinate relative to the viewport
        y: Y coordinate relative to the viewport
        browser: Browser context instance
    
    Returns:
        ActionResult: Result of the action with confirmation message
    """
    try:
        page = await browser.get_current_page()
        await page.mouse.move(x, y)
        message = f"🖱️ Mouse hovering at coordinates ({x}, {y})"
        return ActionResult(extracted_content=message, include_in_memory=True)
    except Exception as e:
        error_message = f"Failed to hover mouse: {str(e)}"
        return ActionResult(error=error_message)

@controller.action(
    'Scroll page using mouse wheel',
    param_model=MouseWheelAction
)
async def mouse_wheel(params: MouseWheelAction, browser: BrowserContext) -> ActionResult:
    """
    Scroll the page using mouse wheel simulation. This function emulates a user scrolling with their physical mouse wheel.
    
    This implementation uses advanced human-like scrolling patterns:
    - Perfect 1px increment scrolling that exactly matches real human mouse behavior
    - Natural acceleration and deceleration within each segment
    - Multiple segments with variable delays between them
    - Subtle hand tremor simulation and occasional skips
    - Probabilistic axis selection for diagonal scrolling
    
    PARAMETER USAGE GUIDE:
    
    delta_y (vertical scrolling):
        - POSITIVE values (e.g. 300) = scroll DOWN the page
        - NEGATIVE values (e.g. -200) = scroll UP the page
        
    
    delta_x (horizontal scrolling):
        - POSITIVE values (e.g. 100) = scroll RIGHT
        - NEGATIVE values (e.g. -100) = scroll LEFT
        - Typically use 0 for normal vertical-only scrolling
        - Use non-zero values only for:
          * Horizontally scrollable containers/carousels
          * Wide tables or spreadsheets
          * Maps or horizontal timelines
          * Mobile-style horizontal navigation
    
    WHEN TO USE THIS FUNCTION:
    
    1. Natural scrolling behavior: Use when you need to simulate real user scrolling (triggers scroll events)
    2. Hover-dependent UI: When scrolling might reveal hover-sensitive elements
    3. Lazy-loading content: When content loads as you scroll (social media feeds, infinite scroll pages)
    4. Precise scroll control: When exact positioning is needed to reveal specific elements
    5. Horizontal scrolling: For interfaces with horizontal scroll components
    
    USAGE TIPS:
    
    - Chain multiple small scrolls rather than one large scroll to simulate natural behavior
    - Combine with mouse positioning before/after scrolling
    - Allow small pauses between scrolls to let content load
    - For infinite scrolling pages, use repeated smaller scrolls (300-500px) with pauses
    - For horizontal scrolling elements, first position the mouse over the element, then use delta_x
    
    Args:
        params: MouseWheelAction with delta_x and delta_y values
        browser: Browser context instance
    
    Returns:
        ActionResult: Result of the action with confirmation message
    """
    try:
        import os
        import logging
        import datetime
        import random
        import traceback
        
        # Set up logging
        log_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "mouse_wheel_actions.log")
        
        # Configure logger
        logger = logging.getLogger("mouse_wheel")
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
        logger.info(f"STARTING NEW MOUSE WHEEL SESSION: {session_start_time}")
        logger.info("="*80)
        logger.info(f"Function parameters: delta_x={params.delta_x}, delta_y={params.delta_y}")
        
        page = await browser.get_current_page()
        logger.info("Retrieved current page from browser context")
        
        # Extract total scroll distance
        total_x = params.delta_x
        total_y = params.delta_y
        logger.info(f"Total scroll distances - X: {total_x}, Y: {total_y}")
        
        # Break total distance into segments (macro-level)
        segments_x = create_segments(int(total_x))
        segments_y = create_segments(int(total_y))
        logger.info(f"Created {len(segments_x)} X segments and {len(segments_y)} Y segments")
        logger.info(f"X segments: {segments_x}")
        logger.info(f"Y segments: {segments_y}")
        
        # Ensure both lists have the same length
        max_len = max(len(segments_x), len(segments_y))
        if len(segments_x) < max_len:
            segments_x.extend([0] * (max_len - len(segments_x)))
            logger.info(f"Extended X segments to match Y length: {len(segments_x)}")
        if len(segments_y) < max_len:
            segments_y.extend([0] * (max_len - len(segments_y)))
            logger.info(f"Extended Y segments to match X length: {len(segments_y)}")
        '''
        # Initialize mouse at a random position on the screen if not already set
        try:
            viewport_size = await page.viewport_size()
            current_mouse_x = random.randint(200, min(viewport_size.get("width", 1000) - 100, 800))
            current_mouse_y = random.randint(200, min(viewport_size.get("height", 800) - 100, 600))
            logger.info(f"Viewport size detected: {viewport_size}")
            logger.info(f"Initialized mouse position to: ({current_mouse_x}, {current_mouse_y})")
        except Exception as e:
            # Fallback in case viewport_size isn't available or has an error
            current_mouse_x = random.randint(200, 800)
            current_mouse_y = random.randint(200, 600)
            logger.warning(f"Failed to get viewport size: {str(e)}. Using fallback mouse position: ({current_mouse_x}, {current_mouse_y})")
        
        # Move mouse to starting position
        await page.mouse.move(current_mouse_x, current_mouse_y)
        logger.info(f"Moved mouse to starting position: ({current_mouse_x}, {current_mouse_y})")
        '''
        # Process each segment with 1px scrolling
        logger.info(f"Starting to process {len(segments_x)} scroll segments")
        for i, (seg_x, seg_y) in enumerate(zip(segments_x, segments_y)):
            logger.info(f"Processing segment {i+1}/{len(segments_x)}: X={seg_x}, Y={seg_y}")
            
            # Log start time for this segment
            segment_start_time = datetime.datetime.now()
            
            # Perform segment scrolling with 1px increments
            segment_scroll_start = datetime.datetime.now()
            logger.info(f"Starting 1px increment scrolling for segment {i+1}")
            
            # Define a custom scroll function with logging
            async def scroll_segment_with_logging(page, segment_x, segment_y):
                """Modified version of scroll_segment_with_1px_increments that includes logging"""
                # Calculate total pixels to scroll (Manhattan distance)
                total_pixels = abs(segment_x) + abs(segment_y)
                if total_pixels == 0:
                    logger.info("Segment has zero pixels to scroll, skipping")
                    return
                    
                # Determine direction for each axis
                x_dir = 1 if segment_x > 0 else -1 if segment_x < 0 else 0
                y_dir = 1 if segment_y > 0 else -1 if segment_y < 0 else 0
                logger.info(f"Scroll directions: X: {x_dir}, Y: {y_dir}")
                
                # Count remaining pixels for each axis
                x_remaining = abs(segment_x)
                y_remaining = abs(segment_y)
                logger.info(f"Initial pixels remaining: X: {x_remaining}, Y: {y_remaining}")
                
                # Initial delay based on real human behavior (2000-2600ms)
                # Only for the first segment
                if random.random() < 0.7:  # 70% chance of initial pause
                    initial_delay = random.uniform(2.0, 2.6)  # 2000-2600ms
                    logger.info(f"Applying initial delay of {initial_delay:.2f} seconds")
                    await asyncio.sleep(initial_delay)
                
                # Begin scrolling
                step_counter = 0
                steps_since_last_pause = 0
                
                # Track scroll clusters for realistic timing
                current_cluster_size = random.randint(10, 20)  # Scrolls before rhythm change
                cluster_count = 0
                logger.info(f"Initial cluster size: {current_cluster_size}")
                
                # Log start of scrolling
                scroll_start_time = datetime.datetime.now()
                logger.info(f"Starting pixel-by-pixel scrolling at {scroll_start_time.strftime('%H:%M:%S.%f')}")
                
                # Use real human delay patterns: 15-18ms base
                while x_remaining > 0 or y_remaining > 0:
                    step_counter += 1
                    steps_since_last_pause += 1
                    cluster_count += 1
                    
                    # Decide which axis to move next (probabilistic)
                    move_x = False
                    move_y = False
                    
                    if x_remaining > 0 and y_remaining > 0:
                        # If both axes have remaining distance, choose probabilistically
                        x_prob = x_remaining / (x_remaining + y_remaining)
                        move_x = random.random() < x_prob
                        move_y = not move_x
                    elif x_remaining > 0:
                        move_x = True
                    elif y_remaining > 0:
                        move_y = True
                        
                    # Perform the 1px scroll
                    wheel_x = x_dir if move_x else 0
                    wheel_y = y_dir if move_y else 0
                    
                    # Occasional micro-tremor (hand instability)
                    tremor_chance = 0.02  # 2% chance
                    tremor_occurred = False
                    if random.random() < tremor_chance:
                        if move_x and random.random() < 0.5:
                            wheel_x = 0  # Skip a pixel occasionally
                            tremor_occurred = True
                        if move_y and random.random() < 0.5:
                            wheel_y = 0  # Skip a pixel occasionally
                            tremor_occurred = True
                    
                    if tremor_occurred and step_counter % 10 == 0:
                        logger.debug(f"Micro-tremor at step {step_counter}: wheel_x={wheel_x}, wheel_y={wheel_y}")
                            
                    # Send the wheel event
                    await page.mouse.wheel(wheel_x, wheel_y)
                    
                    # Update remaining distances
                    if move_x:
                        x_remaining -= 1
                    if move_y:
                        y_remaining -= 1
                    
                    # Log progress every 50 steps
                    if step_counter % 50 == 0:
                        progress_pct = (total_pixels - (x_remaining + y_remaining)) / total_pixels * 100
                        logger.info(f"Scroll progress: {progress_pct:.1f}% - Steps: {step_counter}, Remaining: X={x_remaining}, Y={y_remaining}")
                        
                    # TIMING PATTERNS BASED ON REAL HUMAN DATA
                    
                    # 1. Base delay: 15-18ms (most common in real data)
                    wait_time = random.uniform(0.015, 0.018)  # 15-18ms
                    
                    # 2. Micro-burst chance (7-9ms delay) - observed in real data
                    if random.random() < 0.08:  # 8% chance
                        wait_time = random.uniform(0.007, 0.009)  # 7-9ms
                    
                    # 3. Medium pause (24-33ms) - every ~15-25 scrolls
                    if steps_since_last_pause > random.randint(15, 25) and random.random() < 0.3:
                        wait_time = random.uniform(0.024, 0.033)  # 24-33ms
                        steps_since_last_pause = 0
                        if step_counter % 20 == 0:
                            logger.debug(f"Medium pause at step {step_counter}: {wait_time*1000:.1f}ms")
                    
                    # 4. Longer pause patterns based on real data
                    # These were observed to occur every ~30-40 scroll actions
                    if step_counter % random.randint(30, 40) == 0:
                        pause_type = random.choices(
                            ["medium", "long", "very_long", "cognitive"],
                            weights=[0.4, 0.3, 0.2, 0.1],
                            k=1
                        )[0]
                        
                        if pause_type == "medium":
                            wait_time = random.uniform(0.065, 0.085)  # ~80ms
                            pause_label = "medium"
                        elif pause_type == "long":
                            wait_time = random.uniform(0.09, 0.12)  # ~100ms
                            pause_label = "long"
                        elif pause_type == "very_long":
                            wait_time = random.uniform(0.13, 0.16)  # ~150ms
                            pause_label = "very_long"
                        else:  # cognitive
                            wait_time = random.uniform(0.35, 0.45)  # ~400ms
                            pause_label = "cognitive"
                        
                        logger.debug(f"{pause_label.capitalize()} pause at step {step_counter}: {wait_time*1000:.1f}ms")
                    
                    # 5. Cluster boundary - when we need to change our rhythm
                    if cluster_count >= current_cluster_size:
                        # Create a more noticeable pause between clusters
                        wait_time = random.uniform(0.08, 0.11)  # 80-110ms
                        old_cluster_size = current_cluster_size
                        current_cluster_size = random.randint(10, 20)  # New cluster size
                        cluster_count = 0
                        logger.debug(f"Cluster boundary at step {step_counter}: old size={old_cluster_size}, new size={current_cluster_size}, pause={wait_time*1000:.1f}ms")
                    
                    # Apply the wait time
                    await asyncio.sleep(wait_time)
                
                # Log completion of scrolling
                scroll_end_time = datetime.datetime.now()
                scroll_duration = (scroll_end_time - scroll_start_time).total_seconds()
                logger.info(f"Completed pixel-by-pixel scrolling in {scroll_duration:.2f} seconds, {step_counter} steps")
            
            # Call our custom scrolling function
            await scroll_segment_with_logging(page, seg_x, seg_y)
            
            segment_scroll_end = datetime.datetime.now()
            segment_scroll_duration = (segment_scroll_end - segment_start_time).total_seconds()
            logger.info(f"Completed segment {i+1} scrolling in {segment_scroll_duration:.2f} seconds")
            
            # Random pause between segments (variable "reading" time)
            pause_time = random.uniform(0.2, 1.2)
            logger.info(f"Pausing between segments for {pause_time:.2f} seconds")
            await asyncio.sleep(pause_time)
        
        # Wait for content to load after scrolling
        logger.info("Waiting for page to reach network idle state")
        try:
            network_idle_start = datetime.datetime.now()
            await page.wait_for_load_state('networkidle', timeout=5000)
            network_idle_duration = (datetime.datetime.now() - network_idle_start).total_seconds()
            logger.info(f"Page reached network idle state after {network_idle_duration:.2f} seconds")
        except Exception as e:
            # Ignore timeout errors - pages might never reach network idle
            logger.warning(f"Network idle timeout: {str(e)}")
        
        # Create appropriate message based on scroll direction
        horizontal_msg = f"{abs(total_x)} pixels {'right' if total_x > 0 else 'left'}" if total_x != 0 else ""
        vertical_msg = f"{abs(total_y)} pixels {'down' if total_y > 0 else 'up'}" if total_y != 0 else ""
        
        if horizontal_msg and vertical_msg:
            scroll_msg = f"{horizontal_msg} and {vertical_msg}"
        else:
            scroll_msg = horizontal_msg or vertical_msg
            
        message = f"🖱️ Performed a perfect 1px-increment human-like scroll: {scroll_msg}"
        logger.info(f"Mouse wheel action completed: {message}")
        
        session_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        total_session_duration = (datetime.datetime.now() - datetime.datetime.strptime(session_start_time, "%Y-%m-%d %H:%M:%S.%f")).total_seconds()
        logger.info(f"Total session duration: {total_session_duration:.2f} seconds")
        logger.info("="*80)
        logger.info(f"MOUSE WHEEL SESSION COMPLETED: {session_end_time}")
        logger.info("="*80)
        
        return ActionResult(extracted_content=message, include_in_memory=True)
    except Exception as e:
        try:
            # Try to log the error if logger is defined
            error_message = f"Failed to perform mouse wheel scroll: {str(e)}"
            if 'logger' in locals():
                logger.error(error_message)
                logger.error(f"Exception details: {traceback.format_exc()}")
                
                session_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                logger.error("="*80)
                logger.error(f"MOUSE WHEEL SESSION FAILED: {session_end_time}")
                logger.error("="*80)
        except:
            # If logging itself fails, just continue to return the error
            pass
            
        error_message = f"Failed to scroll in a human-like manner: {str(e)}"
        return ActionResult(error=error_message)

@controller.action(
    'Extract Facebook audience data from table screenshot',
    param_model=ExtractAudienceDataAction
)
async def extract_audience_data(params: ExtractAudienceDataAction, browser: BrowserContext) -> ActionResult:
    """
    Extracts audience data from a Facebook dashboard table screenshot using Claude's Vision API.
    
    This function:
    1. Takes a screenshot of the current page
    2. Sends the screenshot to Claude for analysis via Vision API
    3. Creates a new JSON file or appends to an existing one based on is_first_run parameter
    4. Ensures no duplicate audience_id entries when appending
    
    Args:
        params: ExtractAudienceDataAction with file options
        browser: Browser context instance used to capture the screenshot
    
    Returns:
        ActionResult: Result of the action with confirmation message and file path
    """
    try:
        import os
        import json
        import anthropic
        import logging
        import datetime
        import sys
        import traceback
        from dotenv import load_dotenv
        
        # Set up logging
        log_dir = "/Users/meirsabag/Public/browser_use_ver4_newVersion/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "audience_data_extraction.log")
        
        # Configure logger
        logger = logging.getLogger("audience_extraction")
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
        logger.info(f"STARTING NEW EXTRACTION SESSION: {session_start_time}")
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
            logger.info(f"Created agent files directory: {agent_files_dir}")
            
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
        
        # Detect image format
        if screenshot_data.startswith("iVBORw0KGgo"):
            image_format = "image/png"
            logger.info("Detected image format: PNG")
        else:
            image_format = "image/jpeg"
            logger.info("Detected image format: JPEG (default)")
        
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
                                    "data": screenshot_data
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
            
            # Parse the JSON from the response - extract the portion between ```json and ```
            import re
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
                        "Name": entry.get("name", ""),
                        "Type": entry.get("type", ""),
                        "Availability": entry.get("availability", ""),
                        "Date created": entry.get("date_created", ""),
                        "Audience ID": entry.get("audience_id", "")
                    }
                    audience_data.append(audience_entry)
            
            logger.info(f"Processed {len(audience_data)} audience entries with standardized field names")
            
            # Check if file exists and it's not the first run
            if not params.is_first_run and not file_path:
                logger.error("File path must be provided for subsequent runs")
                return ActionResult(error="File path must be provided for subsequent runs")
            
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
            
            # Write the data to the file - update JSON dump parameters for Hebrew support
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
            
            session_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            logger.info("="*80)
            logger.info(f"EXTRACTION SESSION COMPLETED: {session_end_time}")
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
        try:
            # Try to log the error if logger is defined
            error_message = f"Failed to extract audience data: {str(e)}"
            if 'logger' in locals():
                logger.error(error_message)
                logger.error(f"Exception details: {traceback.format_exc()}")
                
                session_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                logger.error("="*80)
                logger.error(f"EXTRACTION SESSION FAILED: {session_end_time}")
                logger.error("="*80)
        except:
            # If logging itself fails, just continue to return the error
            pass
        
        return ActionResult(error=error_message)

@controller.action('Generate custom prompt for agent')
async def generate_custom_prompt(browser: BrowserContext) -> ActionResult:
    """
    DO NOT USE THIS ACTION.!!!!! 
    I REPEAT DO NOT USE THIS ACTION.!!!!! 
    IT IS NOT SUPPOSED TO BE USED BECAUSE THIS TOOL IS UNDER DEVELOPMENT AND NOT READY YET.
    
    Generate a custom prompt as an instruction for the agent's language model.
    This action should only be used when all stopping conditions have been met
    and the agent needs to perform actions beyond its current capabilities.
    
    Args:
        browser: Browser context instance
    
    Returns:
        ActionResult: Result containing the generated prompt
    """
    try:
        # Hardcoded prompt template
        prompt = """
        [AGENT INSTRUCTION]
        You've completed your primary tasks and need to take additional actions.
        
        Now you should:
        1. Analyze the current webpage state
        2. Determine appropriate next steps
        3. Execute actions beyond your standard capabilities
        4. Report back with your findings and actions taken
        
        Remember to maintain context of your previous actions and goals.
        [END INSTRUCTION]
        """
        
        message = "Generated custom prompt for agent execution"
        
        # Return the prompt in the ActionResult with special metadata
        return ActionResult(
            extracted_content=prompt,
            include_in_memory=True,
            metadata={"type": "agent_prompt", "purpose": "extended_capabilities"}
        )
    except Exception as e:
        error_message = f"Failed to generate custom prompt: {str(e)}"
        return ActionResult(error=error_message)

@controller.action('Check if scrolling should continue or stop based on page analysis')
async def check_condition_stop_page_wheel(browser: BrowserContext) -> ActionResult:
    """
    Analyzes the current page screenshot to determine whether to continue scrolling vertically
    or stop based on the condition of the scroll bar and visible content.
    
    This function:
    1. Takes a screenshot of the current page
    2. Loads training images for Claude Vision API context
    3. Sends the screenshot and training images to Claude for analysis
    4. Parses the response to determine if scrolling should continue or stop
    5. Returns the decision and appropriate scroll parameters if needed
    
    Args:
        browser: Browser context instance used to capture the screenshot
    
    Returns:
        ActionResult: Result containing the scroll decision (CONTINUE/STOP) and scroll parameter
                     if applicable, to help the agent decide whether to continue scrolling
    """
    try:
        import os
        import anthropic
        import logging
        import datetime
        import re
        import base64
        import traceback
        from dotenv import load_dotenv
        
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