from browser_use import ActionResult
from browser_use.browser.context import BrowserContext
from pydantic import BaseModel, Field
from typing import Optional, List, Tuple  # Added Tuple
import random
import math
import asyncio
import base64  # Keep if used within, otherwise remove
import datetime
import os
import logging
import traceback

class MouseWheelAction(BaseModel):
    delta_x: float = Field(0, description="Pixels to scroll horizontally (positive for right, negative for left). For most websites, use 0 for vertical-only scrolling.")
    delta_y: float = Field(..., description="Pixels to scroll vertically (positive for down, negative for up). Typical values: 100-300 for small scrolls, 500-800 for larger scrolls.")

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

# Helper function to create segments for natural scrolling
def create_segments(total_distance: int) -> List[int]:
    """ Break total scroll distance into natural segments. """
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

# Helper function with logging for scrolling
async def _scroll_segment_with_logging(page, segment_x: int, segment_y: int, logger=None):
    """Modified version of scroll_segment_with_1px_increments that includes logging"""
    # Calculate total pixels to scroll (Manhattan distance)
    total_pixels = abs(segment_x) + abs(segment_y)
    if total_pixels == 0:
        if logger:
            logger.info("Segment has zero pixels to scroll, skipping")
        return
        
    # Determine direction for each axis
    x_dir = 1 if segment_x > 0 else -1 if segment_x < 0 else 0
    y_dir = 1 if segment_y > 0 else -1 if segment_y < 0 else 0
    if logger:
        logger.info(f"Scroll directions: X: {x_dir}, Y: {y_dir}")
    
    # Count remaining pixels for each axis
    x_remaining = abs(segment_x)
    y_remaining = abs(segment_y)
    if logger:
        logger.info(f"Initial pixels remaining: X: {x_remaining}, Y: {y_remaining}")
    
    # Initial delay based on real human behavior (2000-2600ms)
    # Only for the first segment
    if random.random() < 0.7:  # 70% chance of initial pause
        initial_delay = random.uniform(2.0, 2.6)  # 2000-2600ms
        if logger:
            logger.info(f"Applying initial delay of {initial_delay:.2f} seconds")
        await asyncio.sleep(initial_delay)
    
    # Begin scrolling
    step_counter = 0
    steps_since_last_pause = 0
    
    # Track scroll clusters for realistic timing
    current_cluster_size = random.randint(10, 20)  # Scrolls before rhythm change
    cluster_count = 0
    if logger:
        logger.info(f"Initial cluster size: {current_cluster_size}")
    
    # Log start of scrolling
    scroll_start_time = datetime.datetime.now()
    if logger:
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
        
        if tremor_occurred and logger and step_counter % 10 == 0:
            logger.debug(f"Micro-tremor at step {step_counter}: wheel_x={wheel_x}, wheel_y={wheel_y}")
                
        # Send the wheel event
        await page.mouse.wheel(wheel_x, wheel_y)
        
        # Update remaining distances
        if move_x:
            x_remaining -= 1
        if move_y:
            y_remaining -= 1
        
        # Log progress every 50 steps
        if logger and step_counter % 50 == 0:
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
            if logger and step_counter % 20 == 0:
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
            
            if logger:
                logger.debug(f"{pause_label.capitalize()} pause at step {step_counter}: {wait_time*1000:.1f}ms")
        
        # 5. Cluster boundary - when we need to change our rhythm
        if cluster_count >= current_cluster_size:
            # Create a more noticeable pause between clusters
            wait_time = random.uniform(0.08, 0.11)  # 80-110ms
            old_cluster_size = current_cluster_size
            current_cluster_size = random.randint(10, 20)  # New cluster size
            cluster_count = 0
            if logger:
                logger.debug(f"Cluster boundary at step {step_counter}: old size={old_cluster_size}, new size={current_cluster_size}, pause={wait_time*1000:.1f}ms")
        
        # Apply the wait time
        await asyncio.sleep(wait_time)
    
    # Log completion of scrolling
    scroll_end_time = datetime.datetime.now()
    scroll_duration = (scroll_end_time - scroll_start_time).total_seconds()
    if logger:
        logger.info(f"Completed pixel-by-pixel scrolling in {scroll_duration:.2f} seconds, {step_counter} steps")

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
      if logger and 'file_handler' in locals():
           try:
               logger.removeHandler(file_handler)
               file_handler.close()
           except Exception as close_err:
               print(f"Error closing logger handler: {close_err}") # Non-critical, just print
