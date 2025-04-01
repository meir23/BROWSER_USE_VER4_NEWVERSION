#!/usr/bin/env python3
"""
Logging Utilities Module

This module provides unified logging functions for the Gemini to Computer Use integration.
It centralizes logging functionality to keep the main code files cleaner while maintaining
comprehensive logging capabilities.
"""

import os
import sys
import logging
import json
from datetime import datetime
from io import StringIO

# Directory for storing integration logs
INTEGRATION_LOG_DIR = "integration_logs"
os.makedirs(INTEGRATION_LOG_DIR, exist_ok=True)

# Directory for storing regular logs
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def log_integration_step(step_name, data, log_dir=INTEGRATION_LOG_DIR):
    """
    Log integration steps to a file for tracking the process.
    
    Args:
        step_name (str): Name of the integration step
        data (any): Data to log (will be converted to string)
        log_dir (str): Directory to store log files
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{step_name}_{timestamp}.log")
    
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            if isinstance(data, (dict, list)):
                json.dump(data, f, indent=2, default=str)
            else:
                # Check if this is an OpenAI API response object
                if hasattr(data, 'model_dump_json'):
                    # This is likely a Pydantic model from OpenAI's response
                    f.write(data.model_dump_json(indent=2))
                elif hasattr(data, '__dict__'):
                    # For objects that have a __dict__ but not model_dump_json
                    try:
                        json.dump(data.__dict__, f, indent=2, default=str)
                    except (TypeError, OverflowError):
                        # Fallback for objects that aren't JSON serializable
                        f.write(str(data))
                else:
                    f.write(str(data))
        logging.info(f"{step_name} logged to: {log_file}")
    except Exception as e:
        logging.error(f"Failed to log {step_name}: {e}")


def log_request(data, log_dir=LOGS_DIR):
    """
    Logs the request data to a file.
    
    Args:
        data (dict): Request data to log
        log_dir (str): Directory to store log files
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a timestamp for the log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"request_{timestamp}.json")
    
    # Write the request data to the log file
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"Request logged to: {log_file}")


def log_response(response, log_dir=LOGS_DIR):
    """
    Logs the response data to a file.
    
    Args:
        response (str): Response text to log
        log_dir (str): Directory to store log files
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a timestamp for the log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"response_{timestamp}.txt")
    
    # Write the response text to the log file
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(response)
    
    print(f"Response logged to: {log_file}")


class GeminiCapture:
    """
    Class to capture output from Gemini for further processing.
    """
    def __init__(self):
        self.full_response = ""
    
    def capture(self, text_chunk):
        """Capture text chunks from Gemini response."""
        self.full_response += text_chunk
        # Echo to console
        print(text_chunk, end="")


def capture_stdout(func, *args, **kwargs):
    """
    Capture stdout during a function call.
    
    Args:
        func: Function to call with captured stdout
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        str: Captured output
    """
    # Backup stdout
    original_stdout = sys.stdout
    
    try:
        # Redirect stdout to capture the output
        capture_buffer = StringIO()
        sys.stdout = capture_buffer
        
        # Call the function
        func(*args, **kwargs)
        
        # Get the captured output
        captured_output = capture_buffer.getvalue()
        
    finally:
        # Restore stdout
        sys.stdout = original_stdout
    
    return captured_output 