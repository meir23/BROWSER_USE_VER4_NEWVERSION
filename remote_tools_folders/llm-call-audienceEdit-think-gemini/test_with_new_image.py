"""
Test script for the enhanced llm_caller.py

This script demonstrates how to use the modified generate function with:
1. A custom image path
2. Custom text input

It copies one of the existing training images with a new name for testing.
"""

import os
import shutil
from llm_caller import generate

# Create a test directory if it doesn't exist
test_dir = "test_images"
os.makedirs(test_dir, exist_ok=True)

# Copy an existing training image with a new name for testing
source_image = "adset_training_images/1.png"
test_image = os.path.join(test_dir, "test_campaign_image.png")
shutil.copy(source_image, test_image)

print(f"Copied test image to: {test_image}")

# Define the test text (same as in the examples for validation)
test_text = "The task is to run the campaign with a lookalike audience."

print("Running test with custom image and text...")
print("-" * 80)

# Call the generate function with our test image and text
generate(user_image_path=test_image, user_text=test_text)

print("-" * 80)
print("Test completed.") 