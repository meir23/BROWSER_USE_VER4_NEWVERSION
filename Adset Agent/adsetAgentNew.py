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

    # Create a single shared browser context for both agents
    browser_context = await browser.new_context()

    # Define the main task for the Adset Agent
    # This task should leverage the new actions:
    # 'initialize_computer_agent' and 'run_computer_vision_request'
    # Define a proper URL for Facebook Ads Manager
    ads_manager_url =  "https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=540298900922161&business_id=671989160822743&global_scope_id=671989160822743&nav_entry_point=lep_237&nav_source=unknown"
    target_campaign_name = " אין - לידים וובינר - רימרקטינג 20.9" # Note: RTL characters might need careful handling if matching text, prioritize vision.

    # REVISED TASK for Agent 1 (No Vision): Find, Duplicate Campaign, Handle Dialog
    task_for_campaign_duplicator_agent = f"""
    Your primary goal is to:
    1. Find the campaign named '{target_campaign_name}' in the list.
    2. Select the checkbox next to this campaign using its index.
    3. Click the main 'Duplicate' button using its index.
    4. Handle the duplication dialog that appears by clicking the 'Duplicate' button *inside* the dialog.
    5. Finish the task by calling `done()` immediately after successfully clicking the 'Duplicate' button *within the dialog*.

    INTERACTION STRATEGY (Apply this for all clicks and inputs):
    1.  **Attempt Index First:** Try the action (e.g., `click_element`) using the element `index` you deem most likely based on the current page structure and the goal. Use `scroll_page` if needed.
    2.  **Retry Index on Failure:** If the first attempt returns an error, analyze the error message and context, then try the *same* action **one** more time with the next best `index`.

    INSTRUCTIONS:
    A.  **Navigation:** Navigate to the Facebook Ads Manager campaigns page: {ads_manager_url}.
    B.  **Find and Select Campaign:**
        *   Locate the campaign named '{target_campaign_name}'. Use `scroll_page` repeatedly if needed.
        *   Apply the Interaction Strategy to click the checkbox element (e.g., index 93 based on previous run) next to the campaign name '{target_campaign_name}'.
    C.  **Click Main Duplicate Button:**
        *   Apply the Interaction Strategy to click the main 'Duplicate' button (e.g., index 47 based on previous run). Assume the checkbox was successfully selected.
    D.  **Handle Duplication Dialog:**
        *   A dialog box should appear after step C. It likely contains options and another 'Duplicate' button, typically at the bottom.
        *   Identify the 'Duplicate' button *within this dialog*. It will have a different index than the main one. You will need to estimate its index based on its likely position (e.g., bottom right of the dialog, possibly a high index number if the page has many elements).
        *   Apply the Interaction Strategy to click this *dialog* 'Duplicate' button.
    E.  **Error Handling (General):**
        *   If any action fails after the retry (especially clicking the checkbox or the main duplicate button), call `done(success=false)`.
        *   If the *dialog* 'Duplicate' button click fails (e.g., 'not clickable' or 'not found'), analyze the state. Perhaps the main duplicate click didn't open the dialog correctly. Call `done(success=false)`.
    F.  **Completion:** The task is considered complete **IF AND ONLY IF** the action to click the 'Duplicate' button *within the dialog* (Step D) returns a success status from the browser interaction tool. As soon as that action successfully executes, immediately call `done(success=True)`. No further verification of screen change is needed for *this* agent. If the dialog duplicate click fails after retries, call `done(success=false)`.
    """

    try:
        # --- Agent 1 Setup and Run ---
        print("Instantiating Adset Agent 1...")
        campaign_duplicator_agent = Agent(
            task=task_for_campaign_duplicator_agent,
            llm=llm,
            browser_context=browser_context,  # <-- Use shared browser_context instead of browser
            controller=controller,
            use_vision=True,
            max_actions_per_step=100
        )
        # Consider using different paths if you want separate history for each agent ==> WE DO THAT IN ITERATION 4
        #adset_agent1.settings.save_conversation_path = "/Users/meirsabag/Public/browser_use_ver4_newVersion/history/agent1" 
        #adset_agent1.settings.available_file_paths = ["/Users/meirsabag/Public/browser_use_ver4_newVersion/history/agent1"]
        #os.makedirs(adset_agent1.settings.save_conversation_path, exist_ok=True) # Ensure directory exists

        print("Running Adset Agent 1...")
        result1 = await campaign_duplicator_agent.run()
        print("\n--- Adset Agent 1 Run Result ---")
        print(result1)
        print("--- Adset Agent 1 Finished ---")

        # Reduce delay to 5 seconds
        print("\nWaiting for 5 seconds for page load after duplication...")
        await asyncio.sleep(5)
        print("Wait finished. Proceeding with Agent 2.")

        # --- Agent 2 Setup and Run ---
        # REVISED Task for Agent 2: Navigate, Scroll, and Visually Verify Audience Section
        task_for_adset_audience_modifier_agent = f"""
        Your primary goal is to:
        1. Verify you are starting from the Campaign editing screen (this is assumed after Agent 1 and the delay).
        2. Navigate to the Ad Set editing screen using index-based clicks (multi-attempt: top nav then left panel).
        3. Once navigation is presumed successful, Find the 'Audience' section" to locate the 'Audience' configuration section. and "Custom audiences" section header/label (or the area showing "None" below it) to expand it and reveal the search options.
        4. Finish the task by calling `done()` only after successful visual confirmation.

       
        INSTRUCTIONS:
        1. Scroll down to Find the 'Audience' section and locate the 'Audience' configuration section.
        2. Apply the Interaction Strategy to click the "Custom audiences" section header/label (or the area showing "None" below it) to expand it and reveal the search options.
        3.  **Completion:** The task is considered complete **IF AND ONLY IF**  confirms the **custom audiences** section is visible. As soon as that successful verification is confirmed, immediately call `done(success=True, text='Successfully navigated to Ad Set and visually verified the Audience section.')`.


        Instructions when you need to scroll to reach the Audience or Custom audiences section:
        - You follow the text you received in the input where the label [Current state starts here]
        - If you have <div true;0;button>Custom audiences in the input then choose the scroll_to_text action with the Custom audiences parameter
        - If you don't have the <div true;0;button>Custom audiences input then choose the action of moving the mouse to the middle of the screen and scrolling with some number and then repeat the same instructions in your next step.


        """

        print("\nInstantiating Adset Agent 2...")
        adset_audience_modifier_agent = Agent(
            task=task_for_adset_audience_modifier_agent,
            llm=llm,
            browser_context=browser_context,  # <-- Use shared browser_context instead of browser
            controller=controller,
            use_vision=True,
            max_actions_per_step=50
        )
        # Configure settings for agent 2 (e.g., separate history path) ==> WE DO THAT IN ITERATION 4
        adset_audience_modifier_agent.settings.save_conversation_path = "/Users/meirsabag/Public/browser_use_ver4_newVersion/history"
        #adset_agent2.settings.available_file_paths = ["/Users/meirsabag/Public/browser_use_ver4_newVersion/history/agent2"]
        #os.makedirs(adset_agent2.settings.save_conversation_path, exist_ok=True) # Ensure directory exists

        print("Running Adset Agent 2...")
        result2 = await adset_audience_modifier_agent.run()
        print("\n--- Adset Agent 2 Run Result ---")
        print(result2)
        print("--- Adset Agent 2 Finished ---")


         # Reduce delay to 5 seconds
        print("\nWaiting for 5 seconds for page load after duplication...")
        await asyncio.sleep(5)
        print("Wait finished. Proceeding with Agent 2.")

        # --- Agent 3 Setup and Run ---
        # REVISED Task for Agent 2: Navigate, Scroll, and Visually Verify Audience Section
        agent3_task = f"""
        Your main goal is:
        1. Check that you are starting from the adset editing screen
        2. Make a final approval of the project by clicking Publish or Close
        3. Get confirmation of the click by returning to the advertising campaign screen
        4. Manage errors by saying that if it is not possible to click the Publish or Close button, then say an error and choose a termination action.

        Instructions:
        1. Follow the instructions for clicking one of the action buttons, which are Publish or Close
        2. Then follow the instructions for clicking the Publish or Close action button

        Instructions for when you need to finish the replication and click one of the action buttons, which are Publish or Close or Discard draft:
        - You follow the text you received in the input where there is <div button;0>Publish/>
        - If it exists and if you see in the screenshot you received that the button is indeed available, then choose the action of clicking with the parameter, which is the index number that appears next to the text <div button;0>Publish/>
        - If the input <div button;0>Publish/> does not exist, then look for the input <div button;0>Close/>. If this input exists, then click on it and with the parameter, which is the number in the square brackets that is next to the <div button;0>Close/>
        If this does not exist either, then say an error in capital letters and finish.

        Instructions for operation after clicking the Publish or Close action button:
        - After clicking the Publish or Close button, you will activate a 20-second wait action.
        - After that, if for some reason you have a dialog screen, then always choose to confirm it despite any optimization suggestions or warnings.
        - After that, you will again choose the 20-second wait action
        - After that, you will see that you are back on the advertising dashboard. You can tell this by the image you received and by the prefix of the url, which is: dsmanager.facebook.com/adsmanager/manage
        - After all these conditions have been met, then choose the Done action and you are done.
        """

        print("\nInstantiating Adset Agent 3...")
        agent3 = Agent(
            task=agent3_task,
            llm=llm,
            browser_context=browser_context,  # <-- Use shared browser_context instead of browser
            controller=controller,
            use_vision=True,
            max_actions_per_step=50
        )
        # Configure settings for agent 2 (e.g., separate history path) ==> WE DO THAT IN ITERATION 4
        adset_audience_modifier_agent.settings.save_conversation_path = "/Users/meirsabag/Public/browser_use_ver4_newVersion/history"
        #adset_agent2.settings.available_file_paths = ["/Users/meirsabag/Public/browser_use_ver4_newVersion/history/agent2"]
        #os.makedirs(adset_agent2.settings.save_conversation_path, exist_ok=True) # Ensure directory exists

        print("Running Adset Agent 3...")
        result3 = await agent3.run()
        print("\n--- Adset Agent 3 Run Result ---")
        print(result3)
        print("--- Adset Agent 3 Finished ---")



    except Exception as e:
        print(f"An error occurred while running an Adset Agent: {e}")
    finally:
        # Close the shared browser context first
        await browser_context.close()
        print("Closing browser...")
        await browser.close()
        print("Browser closed.")

if __name__ == "__main__":
    asyncio.run(run_adset_agent())















# ------------ THIS IS THE ORIGINAL TASK BEFORE WE CREATE ALL THE AGENTS ----------------------
'''

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


'''



    