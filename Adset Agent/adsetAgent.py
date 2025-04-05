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
    Sets up and runs the Adset Agent for duplicating a campaign and setting a Lookalike audience.
    """
    # Configure your LLM
    #llm = ChatOpenAI(model="gpt-4o") # Example LLM
    #llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
    llm = ChatAnthropic(model="claude-3-7-sonnet-20250219")
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
    ads_manager_url =  "https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=540298900922161&business_id=671989160822743&global_scope_id=671989160822743&nav_entry_point=lep_237&nav_source=unknown"
    target_campaign_name = " אין - לידים וובינר - רימרקטינג 20.9" # Note: RTL characters might need careful handling if matching text, prioritize vision.

    # REVISED TASK for Duplication and Lookalike Audience
    task = f"""
    Your primary goal is to:
    1. Find the campaign named '{target_campaign_name}'.
    2. Duplicate this campaign.
    3. In the Ad Set of the NEWLY DUPLICATED campaign, change the audience to use a Lookalike audience.
    4. Publish the duplicated campaign with the Lookalike audience.

    **CRITICAL RULE:** If the `run_computer_vision_request` action successfully returns coordinates (x, y) for a target element, your **immediate next action MUST** be the corresponding coordinate-based action (e.g., `click_element_at_coordinates`, `input_text_at_coordinates`) using those exact coordinates. **DO NOT** use an index-based action in the step immediately following a vision call that provided coordinates.

    INTERACTION STRATEGY (Apply this for all clicks and inputs, following the Critical Rule above):
    1.  **Attempt Index First:** Try the action (e.g., `click_element`, `input_text`) using the element `index` you deem most likely based on the current context and screenshot.
    2.  **Retry Index on Failure:** If the first attempt returns an error (e.g., element not found, not clickable), analyze the error and context, then try the *same* action **one** more time with the next best `index`.
    3.  **Fallback to Coordinates:** If the second index-based attempt also fails, you MUST then use the `run_computer_vision_request` action to obtain the precise coordinates for the target element (provide a clear description like "Find coordinates for the checkbox next to campaign '{target_campaign_name}'"). (The Critical Rule applies here).
    4.  **Vision for Verification:** Independently use `run_computer_vision_request` to visually verify the page state after critical steps (e.g., after selecting the campaign, after duplicating, after selecting the audience, before publishing) or when unsure. Specify what you need to confirm (e.g., "Verify checkbox next to '{target_campaign_name}' is checked", "Verify 'Duplicate' button is active", "Verify Lookalike audience '...' is selected"). (The Critical Rule applies here if coordinates are returned).

    INSTRUCTIONS:
    A.  **Initialization:** First, call 'initialize_computer_agent'.
    B.  **Navigation:** Navigate to the Facebook Ads Manager campaigns page: {ads_manager_url}.
    C.  **Find and Select Campaign:**
        *   Visually locate the campaign named '{target_campaign_name}'. Use `scroll_page` if necessary. Use `run_computer_vision_request` task="Find campaign named '{target_campaign_name}'" if needed to get its location.
        *   Apply the Interaction Strategy to click the checkbox directly to the left of the campaign name '{target_campaign_name}'.
        *   **Verify Selection:** Use `run_computer_vision_request` task="Verify checkbox next to '{target_campaign_name}' is checked AND the 'Duplicate' button is now active/enabled".
    D.  **Duplicate Campaign:**
        *   Apply the Interaction Strategy to click the 'Duplicate' button.
        *   **Verify Duplication:** Wait briefly. Use `run_computer_vision_request` task="Verify that a new campaign draft, likely named '{target_campaign_name} - Copy', has appeared or that the view has changed to an editing screen.".
    E.  **Navigate to Duplicated Ad Set:**
        *   Identify the newly created campaign draft (e.g., '{target_campaign_name} - Copy').
        *   Visually locate the Ad Set name within this new campaign (usually below the campaign name or in the editing panel).
        *   Apply the Interaction Strategy to click the Ad Set name (or its associated 'Edit' button/link) to enter the Ad Set editing view.
        *   **Verify Ad Set View:** Use `run_computer_vision_request` task="Verify the page is now editing an Ad Set (look for sections like 'Ad set name', 'Audience', etc.)".
    F.  **Modify Audience to Lookalike:**
        *   Scroll down or use vision (`run_computer_vision_request` task="Find the 'Audience' section") to locate the 'Audience' configuration section.
        *   Apply the Interaction Strategy to click the "Custom audiences" section header/label (or the area showing "None" below it) to expand it and reveal the search options. (Referencing screenshot `...19.38.09.png`).
        *   **Verify Expansion:** Use `run_computer_vision_request` task="Verify the 'Search existing audiences' input box is now visible".
        *   Apply the Interaction Strategy to type "Lookalike" (or "LLA") into the 'Search existing audiences' input box.
        *   From the list of audiences that appears, visually identify and select (click using Interaction Strategy) **one** audience that contains "Lookalike" or "LLA" in its name. Use `run_computer_vision_request` if needed to locate a specific one.
        *   **Verify Lookalike Selection:** Use `run_computer_vision_request` task="Verify that an audience containing 'Lookalike' is now listed under 'Custom audiences'".
    G.  **Verification & Publishing:**
        *   Scroll to the bottom of the page if necessary.
        *   **Before publishing:** Use `run_computer_vision_request` task='Check for any error messages or warnings on the page, especially near the Audience or Budget sections'. Address any critical issues found by navigating back or adjusting settings.
        *   Apply the Interaction Strategy (including the 'not clickable' check) to click the 'Publish' button.
    H.  **Error Handling (General):**
        *   If actions fail even after the coordinate fallback, OR if vision verification shows unexpected results/errors, use `run_computer_vision_request` to analyze the full screen, understand the current state, and decide the best next step.
        *   **Specifically:** If a click action fails with **'not clickable'**, **DO NOT** retry the click immediately. Use `run_computer_vision_request` to **analyze the element's state and surroundings** ("Analyze the state of the 'Publish' button. Is it disabled/grayed out? Are there required fields incomplete?"). Decide the next action based on the analysis (fix error, fill field, or stop).
    I.  **Completion:** The task is complete **ONLY IF** the final 'Publish' action (index or coordinate) **returned a success message** AND a subsequent, **successful** visual check (`run_computer_vision_request`) confirms a success message OR the UI indicates publishing/in review/active. If the final 'Publish' fails (esp. if 'not clickable' and vision confirms it's disabled/blocked), OR if final verification fails, you MUST call `done` with `success=false`.
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
        adset_agent.settings.save_conversation_path = "/Users/meirsabag/Public/browser_use_ver4_newVersion/history"
        adset_agent.settings.available_file_paths = ["/Users/meirsabag/Public/browser_use_ver4_newVersion/history"]
        
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