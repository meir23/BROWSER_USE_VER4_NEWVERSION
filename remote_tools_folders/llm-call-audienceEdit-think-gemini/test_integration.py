#!/usr/bin/env python3
"""
Test script to demonstrate the Gemini to Computer Use integration

This script:
1. Takes a test image from the adset_training_images directory
2. Processes it through Gemini to get instructions
3. Passes those instructions to OpenAI Computer Use API
4. Logs and displays the results

Usage:
  python test_integration.py
"""

import os
import sys
from gemini_to_computer_use import process_with_gemini_and_computer_use

def main():
    print("=" * 80)
    print("TEST: GEMINI TO COMPUTER USE INTEGRATION")
    print("=" * 80)
    
    # Use one of the existing training images
    test_image = "adset_training_images/6.png"
    
    # Verify the image exists
    if not os.path.exists(test_image):
        print(f"Error: Test image not found at {test_image}")
        print("Please update the path to an existing image.")
        sys.exit(1)
    
    print(f"Processing test image: {test_image}")
    print("-" * 80)
    
    # Test prompt
    test_prompt = "Analyze this Facebook Ads Manager screenshot and tell me what steps I should take to configure a lookalike audience."
    
    # Run the integration process
    print(f"Initial prompt: {test_prompt}")
    print("\nInitiating Gemini analysis followed by Computer Use...")
    
    gemini_response, computer_use_response = process_with_gemini_and_computer_use(
        image_path=test_image,
        initial_prompt=test_prompt
    )
    
    # Display summary
    print("\n" + "=" * 80)
    print("INTEGRATION TEST RESULTS")
    print("=" * 80)
    
    if gemini_response and computer_use_response:
        print("✅ Complete integration pipeline successful!")
        print(f"  - Gemini generated {len(gemini_response)} characters of instructions")
        print(f"  - Computer Use API responded with ID: {computer_use_response.id}")
        
        # Check if we got any computer actions
        if hasattr(computer_use_response, 'output') and computer_use_response.output:
            actions = [item for item in computer_use_response.output if item.type == "computer_call"]
            if actions:
                print(f"\nComputer actions suggested ({len(actions)}):")
                for i, action in enumerate(actions, 1):
                    print(f"  {i}. {action.action.type}")
    else:
        print("❌ Integration test encountered issues:")
        if not gemini_response:
            print("  - Gemini analysis failed")
        if not computer_use_response:
            print("  - Computer Use API call failed")
    
    print("\nSee the integration_logs directory for detailed logs.")
    print("=" * 80)

if __name__ == "__main__":
    main() 