# HERE WE CREATE THE BROWSER USE AGENT FOR ADSET MANAGEMENT

import os
import sys
import asyncio

# Add the necessary paths
sys.path.append("/Users/meirsabag/Public/browser_use_ver4_newVersion")
# Ensure the Adset Agent directory itself is in the path to find the controller
sys.path.append("/Users/meirsabag/Public/browser_use_ver4_newVersion/Adset Agent") 

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI # Or whichever LLM you use
# from langchain_anthropic import ChatAnthropic
# from langchain_google_genai import ChatGoogleGenerativeAI

from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig

# Import the custom controller
from adsetAgentController import controller # <-- IMPORT YOUR CONTROLLER



async def run_adset_agent():
    """
    Sets up and runs the Adset Agent with custom computer vision actions.
    """
    # Configure your LLM
    llm = ChatOpenAI(model="gpt-4o") # Example LLM
    #llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
    #llm = ChatAnthropic(model="claude-3-7-sonnet-20250219")
    #llm = ChatGoogleGenerativeAI(model='gemini-1.5-pro', temperature=0.2 , api_key=SecretStr(os.getenv('GEMINI_API_KEY')))
    #llm=ChatOpenAI(base_url='https://api.deepseek.com/v1', model='deepseek-chat', api_key=SecretStr('DEEPSEEK_API_KEY'))




    # Configure the browser (e.g., connect to existing or launch new)
    browser = Browser(config=BrowserConfig(
        headless=False, 
        # Connect to an existing browser instance
        cdp_url="ws://127.0.0.1:9222/devtools/browser/77839dc3-0324-4ce6-a7a9-f3920787e7f1" 
    ))

    # Define the main task for the Adset Agent
    # This task should leverage the new actions:
    # 'initialize_computer_agent' and 'run_computer_vision_request'
    task = """
    Your primary goal is to [Define the overall goal, e.g., 'create a new ad set with specific targeting'].

    INSTRUCTIONS:
    1. First, you MUST call the 'initialize_computer_agent' action to enable visual analysis capabilities.
    2. Navigate to the Facebook Ads Manager Ad Set creation page: [Specific URL].
    3. Use the 'run_computer_vision_request' action whenever you need to identify element locations for clicking or scrolling. Provide a clear instruction like "Find the 'Campaign Name' input field" or "Click the 'Next' button" as the 'task_or_call_id'.
    4. Analyze the response from 'run_computer_vision_request'. It will contain information about the element or suggested actions (like coordinates for a click).
    5. Use standard browser actions (like 'click_element_at_coordinates', 'scroll_page', 'type_text') based on the information received from the vision agent.
    6. [Add more steps specific to the ad set creation process]
    7. If the vision agent indicates it needs more steps (provides a 'call_id'), use that 'call_id' in the subsequent 'run_computer_vision_request' call.
    8. Complete the task by [Define success criteria, e.g., 'saving the ad set'].
    """

    try:
        adset_agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            controller=controller, # <-- PASS THE IMPORTED CONTROLLER HERE
            max_actions_per_step=100 # Adjust as needed
            # You might add other Agent parameters like extend_system_message if needed
        )

        print("Running Adset Agent...")
        result = await adset_agent.run()
        print("\n--- Adset Agent Run Result ---")
        print(result)
        print("-----------------------------")

    except Exception as e:
        print(f"An error occurred while running the Adset Agent: {e}")
    finally:
        print("Closing browser...")
        await browser.close()
        print("Browser closed.")

if __name__ == "__main__":
    asyncio.run(run_adset_agent())