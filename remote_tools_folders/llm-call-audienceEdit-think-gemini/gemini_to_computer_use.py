#!/usr/bin/env python3
"""
Gemini to Computer Use Integration

This module provides an integration between Google's Gemini AI and OpenAI's Computer Use API.
It processes an image with Gemini to generate instructional text, then uses that text
along with the original image as input for the OpenAI Computer Use API.

Flow:
1. Process image and text with Gemini AI to get detailed guidance
2. Pass that guidance as instruction to OpenAI Computer Use
3. The OpenAI Computer Use API will then attempt to perform the actions

Usage:
  python gemini_to_computer_use.py path/to/image.png "Optional task description"
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Import utilities for logging
from utils.logging_utils import (
    log_integration_step,
    capture_stdout,
    INTEGRATION_LOG_DIR
)

# Import the Gemini-based image processor
from llm_caller import generate

# Import the OpenAI Computer Use API caller
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from computer_agent_request import send_initial_computer_request

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def process_with_gemini_and_computer_use(image_path, initial_prompt=None):
    """
    Process an image with Gemini AI first, then send the result to OpenAI Computer Use.
    
    Args:
        image_path (str): Path to the image file
        initial_prompt (str, optional): Initial task description for Gemini
        
    Returns:
        tuple: (Gemini response, OpenAI Computer Use response)
    """
    logging.info(f"Starting integration process for image: {image_path}")
    
    # Convert to absolute path if it's not already
    if not os.path.isabs(image_path):
        image_path = os.path.abspath(image_path)
    
    if not os.path.exists(image_path):
        logging.error(f"Image file not found: {image_path}")
        return None, None
    
    # Default prompt if none provided
    if initial_prompt is None:
        initial_prompt = "Analyze this Facebook Ads Manager screenshot and provide step-by-step instructions on what to click or interact with next."
    
    # STEP 1: Process with Gemini AI
    logging.info("Step 1: Processing with Gemini AI")
    
    # Use capture_stdout utility to capture Gemini's output
    gemini_response = capture_stdout(
        generate,
        user_image_path=image_path, 
        user_text=initial_prompt
    )
    
    # Log the Gemini response
    log_integration_step("gemini_response", gemini_response)
    
    # STEP 2: Process with OpenAI Computer Use
    logging.info("Step 2: Processing with OpenAI Computer Use")
    
    # Prepare and log the request to OpenAI Computer Use API
    computer_use_request = {
        "prompt_text": gemini_response,
        "image_filename": image_path
    }
    log_integration_step("computer_use_request", computer_use_request)
    
    # Send the Gemini output to OpenAI Computer Use API
    computer_use_response = send_initial_computer_request(
        prompt_text=gemini_response,
        image_filename=image_path
    )
    
    # Log the OpenAI Computer Use response
    log_integration_step("computer_use_response", computer_use_response)
    
    # Log the integration completion with metrics
    log_integration_completion_metrics(image_path, initial_prompt, gemini_response, computer_use_response)
    
    return gemini_response, computer_use_response

def log_integration_completion_metrics(image_path, initial_prompt, gemini_response, computer_use_response):
    """Helper function to log integration completion metrics"""
    
    metrics = {
        "image_path": image_path,
        "initial_prompt": initial_prompt,
        "gemini_response_length": len(gemini_response),
        "computer_use_success": computer_use_response is not None,
        "computer_use_response_id": getattr(computer_use_response, "id", "N/A") if computer_use_response else "N/A",
    }
    
    # Count suggested actions if available
    if computer_use_response and hasattr(computer_use_response, "output"):
        metrics["suggested_actions_count"] = len([
            item for item in computer_use_response.output 
            if item.type == "computer_call"
        ])
    else:
        metrics["suggested_actions_count"] = 0
        
    log_integration_step("integration_complete", metrics)

def display_results(gemini_response, computer_use_response):
    """Display formatted results to the console"""
    
    if gemini_response and computer_use_response:
        print("\n✅ Integration process completed successfully!")
        print("  - Gemini analyzed the image and provided instructions")
        print("  - OpenAI Computer Use processed those instructions")
        
        # Display action information if available
        if hasattr(computer_use_response, 'output') and computer_use_response.output:
            actions = [item for item in computer_use_response.output if item.type == "computer_call"]
            if actions:
                print(f"\nComputer Use suggested {len(actions)} action(s):")
                for i, action in enumerate(actions, 1):
                    print(f"  {i}. {action.action.type}")
            
            # Display reasoning if available
            reasoning_items = [item for item in computer_use_response.output if item.type == "reasoning"]
            if reasoning_items:
                print("\nReasoning information provided:")
                for item in reasoning_items:
                    if hasattr(item, 'reasoning') and hasattr(item.reasoning, 'summary'):
                        print(f"  Summary: '{item.reasoning.summary}'")
    else:
        print("\n❌ Integration process encountered errors.")
        if not gemini_response:
            print("  - Gemini AI processing failed.")
        if not computer_use_response:
            print("  - OpenAI Computer Use processing failed.")
    
    print("\nSee logs for details.")

if __name__ == "__main__":
    # Set up command line argument handling
    if len(sys.argv) < 2:
        print("Error: Please provide at least an image path.")
        print(f"Usage: python {sys.argv[0]} path/to/image.png \"Optional task description\"")
        sys.exit(1)
    
    # Get the image path from first argument
    image_path = sys.argv[1]
    
    # Get the text from second argument if provided, otherwise use default
    initial_prompt = None
    if len(sys.argv) > 2:
        initial_prompt = sys.argv[2]
    
    # Run the integration process
    gemini_response, computer_use_response = process_with_gemini_and_computer_use(
        image_path=image_path,
        initial_prompt=initial_prompt
    )
    
    # Display results to the user
    display_results(gemini_response, computer_use_response) 