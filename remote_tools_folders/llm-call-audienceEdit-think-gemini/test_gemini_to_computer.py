#!/usr/bin/env python3
"""
Simple Test Script for Gemini to Computer Use Integration

This script demonstrates the basic functionality of the integration between
Gemini AI and OpenAI Computer Use API by:
1. Using a test image from the adset_training_images directory
2. Calling the integration function
3. Displaying the results

Usage:
  python test_gemini_to_computer.py
"""

import os
import sys
from gemini_to_computer_use import process_with_gemini_and_computer_use

# Use one of the existing training images for testing
TEST_IMAGE = "adset_training_images/6.png"
TEST_PROMPT = "Tell me what to click on to set up a lookalike audience"

def main():
    print("\n" + "=" * 60)
    print("TESTING GEMINI TO COMPUTER USE INTEGRATION")
    print("=" * 60)
    
    # Check if the test image exists
    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Test image not found: {TEST_IMAGE}")
        sys.exit(1)
    
    # Run the integration process
    print(f"📊 Processing test image: {TEST_IMAGE}")
    print(f"🔍 With prompt: '{TEST_PROMPT}'")
    print("-" * 60)
    
    gemini_response, computer_use_response = process_with_gemini_and_computer_use(
        image_path=TEST_IMAGE,
        initial_prompt=TEST_PROMPT
    )
    
    # Display results
    print("\n" + "-" * 60)
    print("RESULTS:")
    
    if gemini_response:
        print("\n✅ Gemini processing successful")
        print(f"→ Generated {len(gemini_response)} characters of instructions")
        print(f"→ First 100 characters: '{gemini_response[:100]}...'")
    else:
        print("\n❌ Gemini processing failed")
    
    if computer_use_response:
        print("\n✅ OpenAI Computer Use processing successful")
        print(f"→ Response ID: {computer_use_response.id}")
        
        # Show actions if available
        if hasattr(computer_use_response, 'output'):
            actions = [item for item in computer_use_response.output if item.type == "computer_call"]
            if actions:
                print(f"→ Found {len(actions)} suggested actions:")
                for i, action in enumerate(actions, 1):
                    print(f"  {i}. {action.action.type}")
            
            # Show reasoning if available
            reasoning_items = [item for item in computer_use_response.output if item.type == "reasoning"]
            if reasoning_items and hasattr(reasoning_items[0], 'reasoning'):
                print(f"→ Found reasoning information")
                if hasattr(reasoning_items[0].reasoning, 'summary'):
                    summary = reasoning_items[0].reasoning.summary
                    if len(summary) > 50:
                        summary = summary[:50] + "..."
                    print(f"  Summary: '{summary}'")
    else:
        print("\n❌ OpenAI Computer Use processing failed")
    
    print("\nTest completed. Check integration_logs directory for detailed logs.")
    print("=" * 60)

if __name__ == "__main__":
    main() 