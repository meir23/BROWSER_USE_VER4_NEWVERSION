#!/usr/bin/env python3
"""
Command-line utility to run the Facebook Ads Manager AI Assistant

Usage:
  python run_with_image.py path/to/image.png "Your task description here"

Example:
  python run_with_image.py adset_training_images/1.png "The task is to run the campaign with a lookalike audience."
"""

import sys
from llm_caller import generate

if __name__ == "__main__":
    # Check if at least an image path is provided
    if len(sys.argv) < 2:
        print("Error: Please provide at least an image path.")
        print(f"Usage: python {sys.argv[0]} path/to/image.png \"Your task description here\"")
        sys.exit(1)
    
    # Get the image path from first argument
    image_path = sys.argv[1]
    
    # Get the text from second argument if provided, otherwise use default
    if len(sys.argv) > 2:
        text = sys.argv[2]
    else:
        text = "The task is to run the campaign with a lookalike audience."
    
    # Run the generator with the provided parameters
    generate(user_image_path=image_path, user_text=text) 