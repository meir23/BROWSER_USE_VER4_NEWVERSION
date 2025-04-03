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
    # Define a proper URL for Facebook Ads Manager
    ads_manager_url = "https://www.facebook.com/adsmanager/manage/campaigns"
    
    task = f"""
    Your primary goal is to create a new 'Traffic' ad set in Facebook Ads Manager with manual setup, name it 'New Traffic Campaign', set the website URL to 'http://www.example.com', add an image, and publish it.

    INTERACTION STRATEGY (Apply this for all clicks and inputs):
    1.  **Attempt Index First:** Try the action (e.g., `click_element`, `input_text`) using the element `index` you deem most likely based on the current context and screenshot.
    2.  **Retry Index on Failure:** If the first attempt returns an error (e.g., element not found, not clickable), analyze the error and context, then try the *same* action **one** more time with the next best `index`.
    3.  **Fallback to Coordinates:** If the second index-based attempt also fails, you MUST then use the `run_computer_vision_request` action to obtain the precise coordinates for the target element (provide a clear description like "Find coordinates for the 'Continue' button"). Following that, use the corresponding coordinate-based action (e.g., `click_element_at_coordinates`, `input_text_at_coordinates`) with the obtained x and y values. Do not attempt the index-based action a third time.
    4.  **Vision for Verification:** Independently of action success/failure, use `run_computer_vision_request` to visually verify the page state after critical steps (like loading a new page section, before publishing) or when you are unsure about the outcome of an action. Specify what you need to confirm (e.g., "Verify the Ad Set settings page is loaded", "Check for error messages before publishing").

    INSTRUCTIONS:
    A.  **Initialization:** First, you MUST call the 'initialize_computer_agent' action.
    B.  **Navigation:** Navigate to the Facebook Ads Manager campaigns page: {ads_manager_url}.
    C.  **Create Campaign:** Apply the Interaction Strategy for each step:
        *   Click the 'Create' button.
        *   Click the 'Traffic' objective.
        *   Click 'Continue'.
        *   Click 'Manual traffic campaign'.
        *   Click 'Continue'.
    D.  **Campaign Settings:** Apply the Interaction Strategy:
        *   Find the 'Campaign name' input field. Input 'New Traffic Campaign'.
    E.  **Ad Set Settings:** [Add detailed steps for Ad Set level, applying the Interaction Strategy]
        *   Ensure 'Website' conversion location is selected (click if necessary).
        *   ... other Ad Set settings ...
        *   Click the 'Next' or equivalent button.
    F.  **Ad Settings:** Apply the Interaction Strategy:
        *   Find the 'Website URL' field. Input 'http://www.example.com'.
        *   **Add Image (Multi-Step):** Apply the Interaction Strategy carefully for each sub-step:
            *   Click the 'Add Media' or 'Add Image' button.
            *   If an upload dialog appears, use vision requests and coordinate clicks to navigate it (e.g., click 'Upload', potentially handle file selection if possible within limitations, click 'Confirm'/'Done'). Use visual verification (`run_computer_vision_request`) to confirm the image appears selected in the Ad preview.
        *   ... other Ad settings ...
    G.  **Verification & Publishing:**
        *   **Before publishing:** Use `run_computer_vision_request` task='Check for any error messages or warnings on the final review page'. Address any issues found.
        *   Apply the Interaction Strategy to click the 'Publish' button.
    H.  **Error Handling (General):** If actions fail even after the coordinate fallback, or if vision verification shows unexpected results or errors, use `run_computer_vision_request` to analyze the full screen, understand the current state, and decide the best next step (which might be retrying, correcting a previous step, or stopping if the task is unrecoverable). If the vision agent provides a 'call_id' for multi-step analysis, use it in the next relevant request.
    I.  **Completion:** The task is complete **ONLY IF** the final 'Publish' action (e.g., `click_element` or `click_element_at_coordinates` targeting 'Publish') **returned a success message** (not an error like 'Element not clickable' or 'not found') **AND** a subsequent, **successful** visual check (`run_computer_vision_request` that did not error out due to `call_id` or other issues) confirms a success message OR the UI indicates the campaign/ad set is publishing/in review/active. If the final 'Publish' action itself fails, OR if the required final visual verification fails or cannot be performed (e.g., due to a `call_id` error), you MUST call `done` with `success=false` and clearly state the point of failure.
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