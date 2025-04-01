import os
import asyncio
from typing import Optional, Dict, Any, Union
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr
from langchain_core.language_models.base import BaseLanguageModel

from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig

# Import custom controller
from remote_tools_folders.custom_controller import controller

class FacebookAdsAgent:
    """
    FacebookAdsAgent: Class for automating Facebook Ads Manager interactions.
    
    This class encapsulates the functionality needed to automate tasks in Facebook Ads Manager
    using a browser automation framework and an LLM (Language Learning Model). The class is designed
    to allow multiple instances to run concurrently, each with its own configuration and browser session.
    
    Key features:
    - Configurable LLM provider and model
    - Customizable browser settings
    - Support for multiple simultaneous instances
    - Proper resource management (initialization and cleanup)
    - Async context manager support
    """
    
    def __init__(
        self,
        task_prompt_path: str = "/Users/meirsabag/Public/browser_use_ver4_newVersion/task-prompt.md",
        behavior_rules_path: str = "/Users/meirsabag/Public/browser_use_ver4_newVersion/anatomic_behavior_rules.md",
        llm_provider: Optional[str] = "anthropic",  # Default provider, can be overridden
        llm_model: Optional[str] = "claude-3-5-sonnet-20240620",  # Default model, can be overridden
        browser_config: Optional[Dict[str, Any]] = None,
        headless: bool = False,
        cdp_url: Optional[str] = "ws://127.0.0.1:9222/devtools/browser/6654550c-b3ba-4d7a-8c19-18de969f753a",
        startpoint_url: Optional[str] = None  # Initial URL for the agent to navigate to (optional) BrowserContext.get_current_page.url
    ):
        """
        Initialize the FacebookAdsAgent with configurable parameters.
        
        This constructor stores the configuration but doesn't initialize resources immediately.
        Actual initialization happens when initialize() is called explicitly or when the agent
        is used as a context manager.
        
        Args:
            task_prompt_path: Path to the file containing the task prompt that guides the agent's actions
            behavior_rules_path: Path to the file containing behavior rules for the agent
            llm_provider: The LLM provider to use ('anthropic', 'openai', 'google', or 'deepseek')
            llm_model: The specific model to use from the selected provider
            browser_config: Optional custom browser configuration as a dictionary
            headless: Whether to run the browser in headless mode (no UI)
            cdp_url: Chrome DevTools Protocol URL for connecting to an existing browser instance
        """
        # Store configuration parameters as instance attributes
        self.task_prompt_path = task_prompt_path
        self.behavior_rules_path = behavior_rules_path
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        
        # Initialize default browser config if none provided
        if browser_config is None:
            # Create a browser configuration with the provided or default values
            self.browser_config = BrowserConfig(
                headless=headless,
                cdp_url=cdp_url
            )
        else:
            # Use the provided browser configuration
            self.browser_config = BrowserConfig(**browser_config)
            
        # These components will be initialized on demand
        # We use None as initial values to indicate they haven't been initialized yet
        self._llm = None          # Language Learning Model
        self._browser = None      # Browser instance
        self._agent = None        # Agent that combines the LLM and browser
    
    def _initialize_llm(self) -> BaseLanguageModel:
        """
        Initialize and return the specified Language Learning Model.
        
        This private method creates an instance of the requested LLM based on the
        provider and model specified during initialization. It handles different 
        initialization parameters for each provider.
        
        Returns:
            BaseLanguageModel: An initialized LLM instance ready to use
            
        Raises:
            ValueError: If an unsupported LLM provider is specified
        """
        # Create the appropriate LLM instance based on the provider
        if self.llm_provider == "anthropic":
            # Anthropic's Claude models
            return ChatAnthropic(model=self.llm_model)
        
        elif self.llm_provider == "openai":
            # OpenAI's models like GPT-4
            return ChatOpenAI(model=self.llm_model)
        
        elif self.llm_provider == "google":
            # Google's Gemini models
            return ChatGoogleGenerativeAI(
                model=self.llm_model, 
                temperature=0.2,  # Lower temperature for more deterministic outputs
                api_key=SecretStr(os.getenv('GEMINI_API_KEY'))  # Get API key from environment variables
            )
        
        elif self.llm_provider == "deepseek":
            # DeepSeek models, accessed via OpenAI-compatible API
            return ChatOpenAI(
                base_url='https://api.deepseek.com/v1',  # DeepSeek's API endpoint
                model=self.llm_model, 
                api_key=SecretStr(os.getenv('DEEPSEEK_API_KEY'))  # Get API key from environment variables
            )
        
        else:
            # If an unsupported provider is specified, raise an error
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    async def initialize(self):
        """
        Initialize the agent components: LLM, browser, and agent instance.
        
        This method:
        1. Initializes the LLM using the configured provider and model
        2. Creates a browser instance with the specified configuration
        3. Reads the task prompt and behavior rules from their files
        4. Creates an Agent instance combining all these components
        
        Returns:
            self: Returns the instance for method chaining
            
        Note:
            This method is called automatically when using the agent as a context manager,
            but can also be called explicitly if needed.
        """
        # Initialize the LLM first
        self._llm = self._initialize_llm()
        
        # Create a browser instance with our configuration
        self._browser = Browser(config=self.browser_config)
        
        # Read task prompt and behavior rules from their respective files
        with open(self.task_prompt_path, "r") as f:
            task_prompt = f.read()
        
        with open(self.behavior_rules_path, "r") as f:
            behavior_rules = f.read()
        
        # Create an Agent instance that combines the LLM, browser, and task details
        self._agent = Agent(
            task=task_prompt,              # The task prompt that guides the agent
            llm=self._llm,                 # The LLM to use for decision making
            browser=self._browser,         # The browser to interact with
            controller=controller,         # Custom controller for additional functionality
            extend_system_message=behavior_rules  # Additional behavior rules for the agent
        )
        
        # Return self to allow method chaining
        return self
    
    async def run_task(self, custom_task: Optional[str] = None) -> str:
        """
        Run a Facebook Ads task using the configured agent.
        
        This method:
        1. Ensures the agent is initialized
        2. Optionally updates the task if a custom one is provided
        3. Executes the task and returns the result
        4. Handles any exceptions that occur during execution
        
        Args:
            custom_task: Optional custom task description to override the default one
            
        Returns:
            str: The result of the task execution or an error message if something went wrong
        """
        # Ensure the agent is initialized before trying to use it
        if self._browser is None or self._agent is None:
            await self.initialize()
        
        try:
            # If a custom task is provided, update the agent's task
            if custom_task:
                self._agent.task = custom_task
                
            # Run the agent and get the result
            result = await self._agent.run()
            return result
            
        except Exception as e:
            # Catch any exceptions and return them as an error message
            return f"Error: {str(e)}"
    
    async def close(self):
        """
        Close the browser and clean up resources.
        
        This method ensures proper cleanup of resources, particularly
        the browser instance which needs to be closed to avoid memory
        leaks and orphaned processes.
        
        Note:
            This method is called automatically when using the agent as a context manager,
            but can also be called explicitly if needed.
        """
        # Only try to close the browser if it exists
        if self._browser:
            # Close the browser to free resources
            await self._browser.close()
            
            # Set components to None to indicate they're no longer available
            self._browser = None
            self._agent = None
    
    async def __aenter__(self):
        """
        Support using the agent as an async context manager.
        
        This magic method is called when the agent is used in an async with statement.
        It initializes the agent components and returns the agent instance.
        
        Returns:
            self: The initialized agent instance
        
        Example:
            async with FacebookAdsAgent() as agent:
                result = await agent.run_task("your task here")
        """
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Clean up when exiting the async context.
        
        This magic method is called when exiting an async with statement.
        It ensures the browser and other resources are properly closed.
        
        Args:
            exc_type: The exception type if an exception was raised in the context
            exc_val: The exception value if an exception was raised in the context
            exc_tb: The traceback if an exception was raised in the context
        """
        await self.close()










# Example usage of the FacebookAdsAgent class
async def example_usage():
    """
    Example function demonstrating how to use the FacebookAdsAgent directly.
    This approach requires explicit initialization and cleanup.
    """
    # Create a Facebook Ads Agent instance with default settings
    agent = FacebookAdsAgent()
    
    try:
        # Initialize the agent explicitly
        await agent.initialize()
        
        # Run a custom task
        result = await agent.run_task(
            "Open new tab and go to Facebook Ads Manager at https://adsmanager.facebook.com/adsmanager/manage/campaigns "
            "and retrieve all data from the ADS TAB"
        )
        
        print("Facebook Ads Data Result:")
        print(result)
        
    finally:
        # Ensure browser is closed, even if an error occurred
        await agent.close()

# Alternative usage with context manager
async def example_with_context():
    """
    Example function demonstrating how to use the FacebookAdsAgent with a context manager.
    This approach handles initialization and cleanup automatically.
    """
    # Create and use the agent in a context manager
    async with FacebookAdsAgent() as agent:
        # Run a task to find a specific campaign and duplicate it
        result = await agent.run_task(
            "Find the campaign named 'x-elad' in the list, select it by checking its checkbox, "
            "and then click the Duplicate button"
        )
        print(result)

# Multiple concurrent agents example
# ===>> TODO: MAKE THIS CLASS THAT CAN BE TOOL FOR EVALUATE LETTA AGENT WITH PARAMS AND FUNCTION TO
#  CREATE MULTI AGENT AND RUN AND TRACK STATS 
async def run_multiple_agents():
    """
    Example function demonstrating how to run multiple agents concurrently.
    This shows the advantage of the class-based approach for parallelism.
    """
    # Create two agent instances with different configurations
    agent1 = FacebookAdsAgent(llm_model="claude-3-5-sonnet-20240620")
    agent2 = FacebookAdsAgent(llm_model="claude-3-7-sonnet-20250219", headless=True)
    
    # Initialize both agents
    await agent1.initialize()
    await agent2.initialize()
    
    try:
        # Run different tasks concurrently
        task1 = agent1.run_task("Get performance data for all active campaigns")
        task2 = agent2.run_task("Get audience insights for the top performing ad")
        
        # Wait for both tasks to complete
        results = await asyncio.gather(task1, task2)
        
        print("Task 1 result:", results[0])
        print("Task 2 result:", results[1])
        
    finally:
        # Clean up resources for both agents
        await agent1.close()
        await agent2.close()

# Run the examples when executed as a script
if __name__ == "__main__":
    # Choose one of the example functions to run
    asyncio.run(example_usage())
    # asyncio.run(example_with_context())
    # asyncio.run(run_multiple_agents())