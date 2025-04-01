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
        cdp_url="ws://127.0.0.1:9222/devtools/browser/de9122e7-8c63-4465-820c-fd4c3068deeb"
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
            open new tab and go to facebook adsmanager in the link: https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=540298900922161&business_id=671989160822743&global_scope_id=671989160822743&nav_entry_point=lep_237&date=2022-05-04_2025-02-04%2Cmaximum&comparison_date=&insights_date=2022-05-04_2025-02-04%2Cmaximum&insights_comparison_date=&nav_source=unknown.
            Your task is to mark the campaign named "x-elad" in the checklist. And only after you have seen that you have made the mark in the right place by seeing the V sign next to the correct name of the campaign in the table, then and only then do you click the Duplicate button.
            
            A note related to understanding how to figure out the correct index number for action: You must be sure that this is the correct campaign name and you can see this according to your screenshot and the relevant number of the square that surrounds it. 
            For example, if the campaign name has index number 95, then notice that number 95 is part of a sequence of numbers in the same row where the difference between them is also one between each square and square, and they must also be visually aligned as you can see from the image in the same row
            According to the relevant square number that surrounds it, you can also deduce what the relevant square number is for the checklist you need since it is on the same row.
            
            An important note regarding your decision to do a sequence of actions: This is a complex task in which each action has consequences. When you give two actions in a sequence, you are necessarily acting on an assumption and not after analyzing the situation following an action, and therefore this can lead to you taking actions on the wrong buttons on the page. Therefore, it is very important that you know how to separate the actions so that you decide on one action at a time and not on a sequence.

            Note that when you look at the image, the correct index number is always the number in the upper left corner of the square that surrounds the element.
            

            Your inference method regarding finding the campaign name in the task for what is on the advertising dashboard: First, you always, always work according to the image you receive. In the image, you will see red squares (as I have already explained to you) with index numbers for each element. But for the inference of finding the campaign name, it is important that you also see in the image that it is written with the exact same name as in the task. In the image, the name should be in the dashboard table itself in the Campaign column. You must not use a content extraction tool to be able to infer or find the name of the campaign on the page from there. Rather, you must work according to the image provided to you and according to the inference method I have just given you.

            A problem with Hebrew that you should be aware of: Sometimes the name of the campaign in your mission description is in Hebrew. Due to interface issues, sometimes it is written backwards and then you may not be able to find the name of the campaign. Therefore, always search for the campaign name either by how it is written to you or by reversing the letters.

            For once, do not refer to actions related to a column in the delivery table.

            REMEMBER: YOUR MAIN GOAL IS TO DUPLICATE THE CAMPAIGN NAMED "x-elad" AND BEFORE YOU DONE AND NOT JUST CLICK ON THE DUPLICATE BUTTON.
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