# Mouse Positioning Functionality for Browser-Use Agent

This documentation explains how to use the mouse positioning functionality that has been added to the Browser-Use agent.

## Overview

The mouse positioning functionality allows the agent to:

1. Move the mouse cursor to specific coordinates on a webpage
2. Perform hover actions at specific coordinates
3. Click at the current mouse position
4. Scroll the page using mouse wheel

This is especially useful for interacting with elements that:
- Only appear on hover
- Require precise positioning
- Need specific mouse movement patterns
- Need scrolling that simulates natural mouse wheel usage

## Available Functions

### 1. Move Mouse to Coordinates

Moves the mouse cursor to the specified X and Y coordinates on the page.

**Parameters:**
- `x` (float): X coordinate relative to the viewport in CSS pixels
- `y` (float): Y coordinate relative to the viewport in CSS pixels
- `steps` (int, optional): Number of intermediate steps for the movement (default: 1)

**Example Task:**
```
Move the mouse cursor to position x=300, y=200 on the page.
```

### 2. Mouse Hover at Coordinates

Moves the mouse to specified coordinates to perform a hover action, which can reveal hover-dependent elements.

**Parameters:**
- `x` (float): X coordinate relative to the viewport
- `y` (float): Y coordinate relative to the viewport

**Example Task:**
```
Hover the mouse over the position x=150, y=300 to reveal the dropdown menu.
```

### 3. Click at Current Position

Clicks the mouse at its current position.

**Example Task:**
```
After moving to the correct position, click the mouse at the current location.
```

### 4. Scroll Using Mouse Wheel

Scrolls the page using the mouse wheel, which can be more natural than programmatic scrolling for some websites.

**Parameters:**
- `delta_x` (float): Pixels to scroll horizontally
  - Positive values (e.g., 100): Scroll RIGHT
  - Negative values (e.g., -100): Scroll LEFT
  - For most standard web pages, use 0 (no horizontal scrolling)
  - Use non-zero values only for horizontal carousels, wide tables, maps, etc.

- `delta_y` (float): Pixels to scroll vertically
  - Positive values (e.g., 300): Scroll DOWN
  - Negative values (e.g., -200): Scroll UP
  - Small scroll: 100-200 pixels
  - Medium scroll: 300-500 pixels
  - Large scroll: 600-1000 pixels

**When to Use Different Scroll Amounts:**

* **Small scrolls (100-300px):**
  - For precise positioning
  - When searching for specific elements
  - For dense content areas where items might be missed
  - For careful navigation of complex interfaces

* **Medium scrolls (300-500px):**
  - For standard page navigation
  - When moving between sections of content
  - For infinite scroll pages with regular content loading

* **Large scrolls (600px+):**
  - To quickly navigate long pages
  - To skip past large sections of irrelevant content
  - When reaching footer/header areas from middle of page

**Example Tasks:**
```
Scroll down the page by 300 pixels using the mouse wheel.
```

```
Scroll up the page by 200 pixels to reveal the navigation menu.
```

```
Position the mouse over the image carousel and scroll right by 150 pixels to view more images.
```

**Best Practices for Mouse Wheel Scrolling:**

1. Use multiple smaller scrolls with pauses rather than one large scroll
2. Position the mouse appropriately before horizontal scrolling
3. Combine with appropriate waits after scrolling to allow content to load
4. For infinite scroll pages, use a pattern of scroll → wait → check → scroll again
5. For horizontally scrollable elements, position the mouse over the element first

**Note:** Mouse wheel scrolling may trigger different events than programmatic scrolling, which can be useful for websites that behave differently with mouse wheel events, especially:
- Lazy-loading content
- Infinite scroll pages
- Custom scroll animations
- Hover effects that appear during scrolling
- Pages with scroll-activated features

## Implementation Details

The functionality is implemented using Playwright's mouse API and integrated into the Browser-Use agent through a custom controller. The implementation ensures proper error handling and follows the existing patterns of the Browser-Use codebase.

## Usage in Tasks

When defining tasks for the agent, you can include instructions to use mouse positioning. For example:

```
Go to the Facebook Ads Manager page and:
1. Move the mouse cursor to the campaign row (around x=400, y=300)
2. Wait for the hover actions to reveal buttons
3. Move to the position of the duplicate button
4. Click at the current position
5. Scroll down 200 pixels using the mouse wheel to see more content
```

## Best Practices

1. Use coordinates relative to the viewport (browser window)
2. Combine with page scrolling for elements that are not in the initial viewport
3. Use steps parameter for smoother movement when needed
4. Allow time between mouse movements and subsequent actions for hover effects to appear
5. Use this functionality when element selectors or indexes are not reliable or when hover actions are specifically needed
6. For scrolling, consider smaller incremental scrolls (100-300 pixels) rather than large jumps for more natural behavior

## Troubleshooting

If mouse movements are not working as expected:

1. Verify the browser window is in focus
2. Check that coordinates are within the viewport dimensions
3. Ensure the page has loaded completely before attempting mouse movements
4. Try using the steps parameter for more reliable movements
5. Combine with waits between actions for pages with dynamic content
6. Note that mouse wheel scrolling might not trigger all the same events as native scrolling on some websites
7. For horizontal scrolling issues, ensure the mouse is positioned over a horizontally scrollable element 