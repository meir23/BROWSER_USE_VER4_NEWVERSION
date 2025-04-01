from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig
import asyncio

async def fetch_facebook_ads_data() -> str:
    """
    Core function that handles the Facebook Ads Manager browser automation.
    This is the low-level implementation that handles browser interaction.
    
    Returns:
        str: The retrieved Facebook Ads data or error message
    """
    #llm = ChatOpenAI(model="gpt-4o")
    #llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
    llm = ChatAnthropic(model="claude-3-7-sonnet-20250219")
    browser = Browser(config=BrowserConfig(
        headless=False,
        cdp_url="ws://127.0.0.1:9222/devtools/browser/4173aafe-26fd-4412-a479-092f7774328a"
    ))
    
    """
            open new tab and go to facebook adsmanager in the link: https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=540298900922161&business_id=671989160822743&global_scope_id=671989160822743&nav_entry_point=lep_237&date=2022-05-04_2025-02-04%2Cmaximum&comparison_date=&insights_date=2022-05-04_2025-02-04%2Cmaximum&insights_comparison_date=&nav_source=unknown Bring me all the data in the ADS TAB of the table dashboard so I can examine them.
            Note that when you look at the image, the correct index number is always the number in the upper left corner of the square that surrounds the element.
    """


    # זו המשימה המלאה אבל נראה לי שזה לא טוב כי האסטרטגיה זה דרך הכפתור שכפול הגדול ולא ב hover
    """ 
    open new tab and go to facebook adsmanager in the link: https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=540298900922161&business_id=671989160822743&global_scope_id=671989160822743&nav_entry_point=lep_237&date=2022-05-04_2025-02-04%2Cmaximum&comparison_date=&insights_date=2022-05-04_2025-02-04%2Cmaximum&insights_comparison_date=&nav_source=unknown.
    Your task is to duplicate a campaign named "x-elad" that is on the dashboard at the address I gave you.

    To do this, you will follow these steps:
    1. Identify the campaign you want to duplicate, if you do not see the name of the campaign then scroll down until you find it. If after scrolling to the end and not finding the name then you finish the task and inform that you did not find the campaign. If you found the campaign then move on to the next step.
    2. Place the mouse on the campaign name square - note that this is an action that is considered a special action, so this is the only action you do and you do not give more than one action in a row.
    3. If you see the small duplicate button located under the xxxx name of the campaign then click on it

    Special notes to keep in mind:
    - To click on the duplicate button of a xxxxxx campaign, it is always found as a row of small buttons under the name of the campaign. These small buttons for: Duplicate, Edit, etc. appear only when the mouse is on the campaign name box. This means that in order to click on the duplicate button, the mouse must hover over the box and only then will the button be available, otherwise you will not see it.
    - Special action = for an action that must be a single action and one or more additional actions must not be attached to it. This is because this is an action that we need to see its impact on the site and decide on the following actions accordingly. Because if we do not do this and there are accidentally several actions in a row, then these actions are determined based on the assumption that there is a high chance that it is incorrect and this will cause an error in performing the task.

    Click on the duplicate button for the campaign named "לידים-אלעד".
    
    Note that when you look at the image, the correct index number is always the number in the upper left corner of the square that surrounds the element.

    
    """





    try:
        agent = Agent(
            task="""
            open new tab and go to facebook adsmanager in the link: https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=540298900922161&business_id=671989160822743&global_scope_id=671989160822743&nav_entry_point=lep_237&date=2022-05-04_2025-02-04%2Cmaximum&comparison_date=&insights_date=2022-05-04_2025-02-04%2Cmaximum&insights_comparison_date=&nav_source=unknown Bring me all the data in the ADS TAB of the table dashboard so I can examine them.
            Note that when you look at the image, the correct index number is always the number in the upper left corner of the square that surrounds the element.
            """,
            llm=llm,
            browser=browser
        )
        
        result = await agent.run()
        return result
        
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        await browser.close()

if __name__ == "__main__":
    result = asyncio.run(fetch_facebook_ads_data())
    print("Facebook Ads Data Result:")
    print(result) 