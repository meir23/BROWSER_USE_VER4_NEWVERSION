import asyncio
from typing import Dict, Any, Optional
from x import FacebookAdsAgent

# Variable to hold the task description - will be replaced with actual value later
task_description = "Default task: Navigate to Facebook Ads Manager and list available campaigns"

# Agent configuration parameters
TASK_PROMPT_PATH = "/Users/meirsabag/Public/browser_use_ver4_newVersion/task-prompt.md"
BEHAVIOR_RULES_PATH = "/Users/meirsabag/Public/browser_use_ver4_newVersion/anatomic_behavior_rules.md"
LLM_PROVIDER = "anthropic"
LLM_MODEL = "claude-3-5-sonnet-20240620"
HEADLESS = False
CDP_URL = "ws://127.0.0.1:9222/devtools/browser/6654550c-b3ba-4d7a-8c19-18de969f753a"

# Optional browser configuration
BROWSER_CONFIG: Optional[Dict[str, Any]] = {
    "headless": HEADLESS,
    "cdp_url": CDP_URL
}

async def run_facebook_ads_task():
    """
    Run the Facebook Ads task using the FacebookAdsAgent class.
    
    This function:
    1. Creates a FacebookAdsAgent instance with explicit constructor parameters
    2. Runs the task defined in the task_description variable
    3. Returns the result from the agent
    
    Returns:
        str: The result of the Facebook Ads task execution
    """
    # Create the agent with explicit constructor parameters
    agent = FacebookAdsAgent(
        task_prompt_path=TASK_PROMPT_PATH,
        behavior_rules_path=BEHAVIOR_RULES_PATH,
        llm_provider=LLM_PROVIDER,
        llm_model=LLM_MODEL,
        browser_config=BROWSER_CONFIG,
        headless=HEADLESS,
        cdp_url=CDP_URL
    )
    
    try:
        # Initialize the agent
        await agent.initialize()
        
        # Run the task using the task description variable
        result = await agent.run_task(task_description)
        return result
    finally:
        # Ensure the agent is properly closed
        await agent.close()



# Main execution
if __name__ == "__main__":
    # Choose which implementation to use
    # result = asyncio.run(run_facebook_ads_task())  # Explicit initialization and cleanup
    result = asyncio.run(run_facebook_ads_task())  # Using context manager
    
    print("Facebook Ads Task Execution Complete")
    print("====================================")
    print("Task description:")
    print(task_description)
    print("\nTask result:")
    print(result) 