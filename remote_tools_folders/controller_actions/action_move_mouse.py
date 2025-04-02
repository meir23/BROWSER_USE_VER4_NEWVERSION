from browser_use import ActionResult
from browser_use.browser.context import BrowserContext
from pydantic import BaseModel, Field
from typing import Optional, List
import traceback # Added for potential error logging consistency
import random
import math
# import logging # Add if planning to log errors within the helper

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

class MouseMoveAction(BaseModel):
    x: float = Field(..., description="X coordinate relative to the viewport in CSS pixels")
    y: float = Field(..., description="Y coordinate relative to the viewport in CSS pixels")
    steps: Optional[int] = Field(1, description="Number of intermediate steps for the movement (default: 1)")

async def perform_move_mouse(params: MouseMoveAction, browser: BrowserContext) -> ActionResult:
    """
    Helper function containing the logic to move the mouse cursor.
    """
    try:
        page = await browser.get_current_page()
        
        if params.steps <= 1:
            # Simple direct movement for single step
            await page.mouse.move(params.x, params.y)
        else:
            # Human-like curved movement for multiple steps
            # First, get current mouse position
            current_position = await page.evaluate("""() => {
                return { x: window.mousePosX || 0, y: window.mousePosY || 0 };
            }""")
            current_x = current_position.get('x', 0)
            current_y = current_position.get('y', 0)
            
            # Generate arc positions for natural movement
            positions = generate_arc_positions(
                current_x, current_y, 
                params.x, params.y, 
                steps=params.steps
            )
            
            # Move through each position in sequence
            for pos_x, pos_y in positions:
                await page.mouse.move(pos_x, pos_y)
                # Small random delay between movements (10-20ms)
                await page.wait_for_timeout(random.randint(10, 20))
        
        message = f"🖱️ Mouse moved to coordinates ({params.x}, {params.y})"
        return ActionResult(extracted_content=message, include_in_memory=True)
    except Exception as e:
        error_message = f"Failed to move mouse: {str(e)}"
        # Optional: Add logging here
        # logging.error(f"Failed to move mouse: {str(e)}\n{traceback.format_exc()}")
        return ActionResult(error=error_message)
