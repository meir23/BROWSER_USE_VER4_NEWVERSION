import os
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig
import asyncio

# Import our custom controller
from remote_tools_folders.custom_controller import controller

async def fetch_facebook_ads_data() -> str:
    """
    Core function that handles the Facebook Ads Manager browser automation.
    This is the low-level implementation that handles browser interaction.
    
    Returns:
        str: The retrieved Facebook Ads data or error message
    """
    #llm = ChatOpenAI(model="gpt-4o")
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
    #llm = ChatAnthropic(model="claude-3-7-sonnet-20250219")
    #llm = ChatGoogleGenerativeAI(model='gemini-1.5-pro', temperature=0.2 , api_key=SecretStr(os.getenv('GEMINI_API_KEY')))
    #llm=ChatOpenAI(base_url='https://api.deepseek.com/v1', model='deepseek-chat', api_key=SecretStr('DEEPSEEK_API_KEY'))

    
    browser = Browser(config=BrowserConfig(
        headless=False,
        cdp_url="ws://127.0.0.1:9222/devtools/browser/6654550c-b3ba-4d7a-8c19-18de969f753a"
    ))
    
    

    try:
        agent = Agent( #used task version 1.1
            task="""

 <taskAndGoal>
Your task and goal is to open a new tab at the link: 
https://adsmanager.facebook.com/adsmanager/audiences?act=540298900922161&business_id=671989160822743&tool=AUDIENCES&nav_entry_point=ads_ecosystem_navigation_menu&nav_source=ads_manager&date=2025-02-27_2025-02-28%2Ctoday.
AFTER YOU LOADED THE URL, THEN YOU MOVE THE MOUSE TO THE CENTER OF THE SCREEN AND YOU DO THAT ONLY ONCE.
And extract the content from all the rows from the audience table that you see on the Facebook Audiences dashboard.
    </taskAndGoal>

    <instructions>
        <![CDATA[
Instructions:
To complete this task, you always need to decide what sequence of actions you decide for the next step.
You decide this by looking at your current screenshot and all the discussion that has taken place so far.
You understand exactly how your previous decision sequence created the current reality as expressed in the screenshot 
and according to this you give the assessment and what needs to be done and the actions to be performed in the next step.

After each vertical scroll operation, you must call the check_condition_stop_page_wheel function to determine whether to continue scrolling or stop. This function is the definitive authority on when you've reached the end of the table.

The check_condition_stop_page_wheel function will return either:
- A "CONTINUE" decision with a specific pixel value (e.g., "500px") that you MUST use exactly for your next scroll
- A "STOP" decision indicating that you've reached the end of the table and should stop scrolling

Always follow the output of this function precisely - do not make your own determination about whether scrolling should continue or stop based on visual inspection of the screenshot.
        ]]>
    </instructions>

    <stoppingConditionRule>
        <![CDATA[
Rule for determining stopping conditions:
The definitive way to determine if you've reached a stopping condition is when the check_condition_stop_page_wheel function returns "STOP".

When the function returns "STOP", this means the scroll bar has reached a position where further scrolling is not required, and you should consider the data extraction complete for the scrolling portion of the task.

Do not attempt to make your own visual determination about whether scrolling should stop - rely exclusively on the output of the check_condition_stop_page_wheel function.
        ]]>
    </stoppingConditionRule>

    <importantRules>
        <rule id="1">
            <![CDATA[
1. Give the table time to load. You can tell if you see a page that is loading if all the audience names have a square surrounding them. 
If there is no square around the audience names in the table, then you are looking at a page that has loaded too soon, 
so choose a wait action or another screenshot or do a very small scroll of 1 px just to give it another spin.
            ]]>
        </rule>
        <rule id="2">
            <![CDATA[
2. An important rule regarding audience sampling - you can see from the screenshot that sometimes the table has many more rows 
(each row has the audience name and information about it) than the screen can accommodate. 
You can see this by the marking that you can scroll. Therefore, it is very important that you know how to scroll the names of the target audiences. 
And this is according to the following rule.
            ]]>
        </rule>
        
         <rule id="3">
            <![CDATA[
3. After each vertical scroll operation, you MUST call the check_condition_stop_page_wheel function to determine next steps.

When this function returns:
- "CONTINUE" with a pixel value (e.g., "CONTINUE 500px"): You MUST use this exact pixel value for your next scroll action. Do not calculate your own value or modify this value.
- "STOP": You must immediately cease scrolling as you've reached the end of the table.

This function has analyzed the position of the scroll bar in relation to the table and provides the optimal scroll distance or stop command. Always follow its guidance exactly.
            ]]>
        </rule>
        
        <rule id="5">
            <![CDATA[
5. You never count how many audiences you have collected so far.
            ]]>
        </rule>
       
        
        <rule id="8">
            <![CDATA[
8. When using the mouse_wheel action to scroll, always use the exact pixel value returned by the check_condition_stop_page_wheel function when it returns "CONTINUE". 

Do not calculate your own scroll values based on row counts - use the value provided by the function. However, to avoid appearing automated, you should slightly modify the exact value by adding or subtracting a small random decimal (between 0.1 and 0.9) from the provided value.

For example, if the function returns "CONTINUE 500px", use a value like 499.7 or 500.3 pixels.
            ]]>
        </rule>
        <rule id="9">
            <![CDATA[
9. When you choose the wait action, always set a random time between 5 and 13 seconds. 
Try not to make it similar to the values ​​of the previous times. 
This is very important to confuse the Facebook algorithm that can identify that it is you browsing the site.
            ]]>
        </rule>
        <rule id="10">
            <![CDATA[
10. - MOST IMPORTANTLY!! The values ​​​​of the mouse movement and mouse scrolling action must never be round numbers, 
but they must always be non-round numbers, preferably decimal and most importantly they must not repeat themselves. 
At the same time, you must not forget the rules that I have already given you on how to set these parameters, 
this is very important.
            ]]>
        </rule>
    </importantRules>

            """,
            llm=llm,
            browser=browser,
            controller=controller, # Use our custom controller 
            max_actions_per_step=200    
            #extend_system_message=open("/Users/meirsabag/Public/browser_use_ver4_newVersion/anatomic_behavior_rules.md").read()
        )
        
        result = await agent.run()
        return result
        
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        await browser.close()



# this is function to run the function from the command line for test purposes.
if __name__ == "__main__":
    result = asyncio.run(fetch_facebook_ads_data())
    print("Facebook Ads Data Result:")
    print(result) 














    ##### 1.0 VERSION #####

"""
            
Your task is to open a new tab and browse to the address: https://adsmanager.facebook.com/adsmanager/audiences?act=540298900922161&business_id=671989160822743&tool=AUDIENCES&nav_entry_point=ads_ecosystem_navigation_menu&nav_source=ads_manager&date=2025-02-27_2025-02-28%2Ctoday.

There you will see in a table all the information about my audiences. You must bring me from there all the content and information that is on this page so that I can receive in text all the information that is in the table

Important rules that you must follow:
1. Give the table time to load. You can tell if you see a page that is loading if all the audience names have a square surrounding them. If there is no square around the audience names in the table, then you are looking at a page that has loaded too soon, so choose a wait action or another screenshot or do a very small scroll of 1 px just to give it another spin.

2. An important rule regarding audience sampling - you can see from the screenshot that sometimes the table has many more rows (each row has the audience name and information about it) than the screen can accommodate. You can see this by the marking that you can scroll. Therefore, it is very important that you know how to scroll the names of the target audiences. And this is according to the following rule.

3. Scrolling the names of the target audiences - to scroll the target audiences, you must place the mouse cursor inside the table (in the center of the screen) and only then scroll. This is important because there are two types of scrolling: Scroll type 1 is scrolling of the entire page, scroll type 2 is of the audience table. By default, it is scroll type 1, so when you want to scroll the names of the target audiences (scroll type 2) you need to move the mouse to the center of the screen. When you set the parameters for vertical scrolling, take into account that each line is 50 pixels high. Based on this figure, set the scrolling so that you have a significant movement.

4. Always be smart and see that if in the previous step you chose vertical scrolling, then you will see that it really moves, and if not, then you will react accordingly.

5. You never count how many audiences you have collected so far.
6. When you choose the mouse movement action, then select the x and y parameters so that on the one hand it will be inside the table and in its center area, but move the mouse to the right part of the screen (the one farthest from the beginning of the axes) so that the mouse cursor is not on an element that creates a small popup screen.
7. After you choose a vertical scrolling action with the mouse, if you enter a large parameter (over 250 pixels) then you should give a long wait time of 10 seconds because it is possible that a lot of elements are loaded following the vertical scrolling and it will take them more time.
8. When you set the parameter of the vertical scrolling action using the mouse, then you must not allow the value of the parameter to be greater than the number of rows in the table that you need to scroll. For example, if you enter 7 rows in the table according to the screenshot, then because the height of each row is 50 pixels, then you must not allow it to be over 350 pixels (because 7 times 50 is 350). On the other hand, you can't have it be exactly according to this calculation because we don't want it to look suspicious that it's always round and precise numbers. So on the one hand, you're below the maximum and on the other hand, you're reducing it to a non-round and random number that at the same time gives a good amount of scrolling to be efficient in scrolling.
9. When you choose the wait action, always set a random time between 5 and 13 seconds. Try not to make it similar to the values ​​of the previous times. This is very important to confuse the Facebook algorithm that can identify that it is you browsing the site.
10. - MOST IMPORTANTLY!! The values ​​of the mouse movement and mouse scrolling action must never be round numbers, but they must always be non-round numbers, preferably decimal and most importantly they must not repeat themselves. At the same time, you must not forget the rules that I have already given you on how to set these parameters, this is very important.


Stopping conditions:
These are the conditions that you stop for this task:
If you see that the scroll bar on the right side of the screen has no more room to go down and is all the way to the end, then that means there's no more room to scroll. In addition (and this is a necessary condition) you simultaneously see in your context that you've extracted the audience information and it appears in your context. You can see that the value (the number itself) of the last audienceID parameter that you extracted matches exactly what you see in your screenshot. If this happens, then you know for sure that you're done and the task has been completed successfully.

The scroll bar is considered down when it is right on the mark of the bottom line of the table. You must not think that the scroll bar is considered to be the lowest in relation to the bottom of the screen. This is because there is always a distance between the bottom border of the table and the bottom of the screen.



            """

    #####




# 1.1 VERSION #####
"""
Your task is to open a new tab and browse to the address: https://adsmanager.facebook.com/adsmanager/audiences?act=540298900922161&business_id=671989160822743&tool=AUDIENCES&nav_entry_point=ads_ecosystem_navigation_menu&nav_source=ads_manager&date=2025-02-27_2025-02-28%2Ctoday.

There you will see in a table all the information about my audiences. You must bring me from there all the content and information that is on this page so that I can receive in text all the information that is in the table

Important rules that you must follow:
1. Give the table time to load. You can tell if you see a page that is loading if all the audience names have a square surrounding them. If there is no square around the audience names in the table, then you are looking at a page that has loaded too soon, so choose a wait action or another screenshot or do a very small scroll of 1 px just to give it another spin.

2. An important rule regarding audience sampling - you can see from the screenshot that sometimes the table has many more rows (each row has the audience name and information about it) than the screen can accommodate. You can see this by the marking that you can scroll. Therefore, it is very important that you know how to scroll the names of the target audiences. And this is according to the following rule.

3. Scrolling the names of the target audiences - to scroll the target audiences, you must place the mouse cursor inside the table (in the center of the screen) and only then scroll. This is important because there are two types of scrolling: Scroll type 1 is scrolling of the entire page, scroll type 2 is of the audience table. By default, it is scroll type 1, so when you want to scroll the names of the target audiences (scroll type 2) you need to move the mouse to the center of the screen. When you set the parameters for vertical scrolling, take into account that each line is 50 pixels high. Based on this figure, set the scrolling so that you have a significant movement.

4. Always be smart and see that if in the previous step you chose vertical scrolling, then you will see that it really moves, and if not, then you will react accordingly.
5. You never count how many audiences you have collected so far.
6. When you choose the mouse movement action, then select the x and y parameters so that on the one hand it will be inside the table and in its center area, but move the mouse to the right part of the screen (the one farthest from the beginning of the axes) so that the mouse cursor is not on an element that creates a small popup screen.
7. After you choose a vertical scrolling action with the mouse, if you enter a large parameter (over 250 pixels) then you should give a long wait time of 10 seconds because it is possible that a lot of elements are loaded following the vertical scrolling and it will take them more time.
8. When you set the parameter of the vertical scrolling action using the mouse, then you must not allow the value of the parameter to be greater than the number of rows in the table that you need to scroll. For example, if you enter 7 rows in the table according to the screenshot, then because the height of each row is 50 pixels, then you must not allow it to be over 350 pixels (because 7 times 50 is 350). On the other hand, you can't have it be exactly according to this calculation because we don't want it to look suspicious that it's always round and precise numbers. So on the one hand, you're below the maximum and on the other hand, you're reducing it to a non-round and random number that at the same time gives a good amount of scrolling to be efficient in scrolling.
9. When you choose the wait action, always set a random time between 5 and 13 seconds. Try not to make it similar to the values ​​of the previous times. This is very important to confuse the Facebook algorithm that can identify that it is you browsing the site.
10. MOST IMPORTANTLY!! The values ​​of the mouse movement and mouse scrolling action must never be round numbers, but they must always be non-round numbers, preferably decimal and most importantly they must not repeat themselves. At the same time, you must not forget the rules that I have already given you on how to set these parameters, this is very important.
11. The most important rule is when you understand that a vertical scrolling action is needed!! When you already understand that you need to do a vertical scrolling action, and when you understand what value you are going to give, then you must divide this value by choosing a sequence of actions one after the other (in the same step) so that the value in each action is the amount you wanted divided by 50. At the same time, it is important that all the parameters are different from each other. I will give you an example: Let's say you wanted to give a value to the parameter of the vertical scrolling action which is 283.7, so instead of one vertical scrolling action with this value you choose a sequence of 50 vertical scrolling actions where each value in each action is between 3 and 7 and each of them is different from the other. That is, it is 3.4, 6.75 and so on.... In addition, the sequence of these actions that you do will always be before the content extraction action if there is one in this step


example for rule 11:example for rule 4:
Action 1/50: {"move_mouse":{"x":738.6,"y":384.3}}
Action 2/50: {"mouse_wheel":{"delta_y":3.7}}
Action 3/50: {"mouse_wheel":{"delta_y":6.5}}
Action 4/50: {"mouse_wheel":{"delta_y":4.8}}
Action 5/50: {"mouse_wheel":{"delta_y":6.6}}
Action 6/50: {"mouse_wheel":{"delta_y":5.6}}
Action 7/50: {"mouse_wheel":{"delta_y":2.3}}
Action 8/50: {"mouse_wheel":{"delta_y":1.7}}
Action 9/50: {"mouse_wheel":{"delta_y":0.4}}
Action 10/50: {"mouse_wheel":{"delta_y":8.9}}
Action 11/50: {"mouse_wheel":{"delta_y":2.3}}
Action 12/50: {"mouse_wheel":{"delta_y":7.2}}
Action 13/50: {"mouse_wheel":{"delta_y":3.9}}
Action 14/50: {"mouse_wheel":{"delta_y":5.8}}
Action 15/50: {"mouse_wheel":{"delta_y":4.3}}
Action 16/50: {"mouse_wheel":{"delta_y":6.9}}
Action 17/50: {"mouse_wheel":{"delta_y":2.8}}
Action 18/50: {"mouse_wheel":{"delta_y":7.4}}
Action 19/50: {"mouse_wheel":{"delta_y":3.2}}
Action 20/50: {"mouse_wheel":{"delta_y":5.9}}
Action 21/50: {"mouse_wheel":{"delta_y":4.7}}
Action 22/50: {"mouse_wheel":{"delta_y":6.3}}
Action 23/50: {"mouse_wheel":{"delta_y":2.9}}
Action 24/50: {"mouse_wheel":{"delta_y":7.8}}
Action 25/50: {"mouse_wheel":{"delta_y":3.4}}
Action 26/50: {"mouse_wheel":{"delta_y":5.7}}
Action 27/50: {"mouse_wheel":{"delta_y":4.2}}
Action 28/50: {"mouse_wheel":{"delta_y":6.8}}
Action 29/50: {"mouse_wheel":{"delta_y":2.6}}
Action 30/50: {"mouse_wheel":{"delta_y":7.3}}
Action 31/50: {"mouse_wheel":{"delta_y":3.8}}
Action 32/50: {"mouse_wheel":{"delta_y":5.4}}
Action 33/50: {"mouse_wheel":{"delta_y":4.6}}
Action 34/50: {"mouse_wheel":{"delta_y":6.7}}
Action 35/50: {"mouse_wheel":{"delta_y":2.4}}
Action 36/50: {"mouse_wheel":{"delta_y":7.6}}
Action 37/50: {"mouse_wheel":{"delta_y":3.5}}
Action 38/50: {"mouse_wheel":{"delta_y":5.3}}
Action 39/50: {"mouse_wheel":{"delta_y":4.9}}
Action 40/50: {"mouse_wheel":{"delta_y":6.2}}
Action 41/50: {"mouse_wheel":{"delta_y":2.7}}
Action 42/50: {"mouse_wheel":{"delta_y":7.5}}
Action 43/50: {"mouse_wheel":{"delta_y":3.6}}
Action 44/50: {"mouse_wheel":{"delta_y":5.2}}
Action 45/50: {"mouse_wheel":{"delta_y":4.4}}
Action 46/50: {"mouse_wheel":{"delta_y":6.4}}
Action 47/50: {"mouse_wheel":{"delta_y":2.5}}
Action 48/50: {"mouse_wheel":{"delta_y":7.7}}
Action 49/50: {"mouse_wheel":{"delta_y":3.3}}
Action 50/50: {"mouse_wheel":{"delta_y":5.5}}

end of example

Stopping conditions:
These are the conditions that you stop for this task:
If you see that the scroll bar on the right side of the screen has no more room to go down and is all the way to the end, then that means there's no more room to scroll. In addition (and this is a necessary condition) you simultaneously see in your context that you've extracted the audience information and it appears in your context. You can see that the value (the number itself) of the last audienceID parameter that you extracted matches exactly what you see in your screenshot. If this happens, then you know for sure that you're done and the task has been completed successfully.

The scroll bar is considered down when it is right on the mark of the bottom line of the table. You must not think that the scroll bar is considered to be the lowest in relation to the bottom of the screen. This is because there is always a distance between the bottom border of the table and the bottom of the screen.
            
To identify if the stopping conditions are indeed occurring, you will notice that the scroll bar of the audience table is considered the lowest, as you can see in the screenshot that the rectangle that surrounds it, so the bottom edge (which is the base of the rectangle) meets the scroll bar and there is no gap between them. Remember this because it is very important because it determines whether you have gone through all the rows in the table.



"""




#########




###### 1.2 VERSION #####


"""

 <taskAndGoal>
        <![CDATA[
Your task and goal is to open a new tab at the link: 
https://adsmanager.facebook.com/adsmanager/audiences?act=540298900922161&business_id=671989160822743&tool=AUDIENCES&nav_entry_point=ads_ecosystem_navigation_menu&nav_source=ads_manager&date=2025-02-27_2025-02-28%2Ctoday.

And extract the content from all the rows from the audience table that you see on the Facebook Audiences dashboard.
        ]]>
    </taskAndGoal>

    <instructions>
        <![CDATA[
Instructions:
To complete this task, you always need to decide what sequence of actions you decide for the next step.
You decide this by looking at your current screenshot and all the discussion that has taken place so far.
You understand exactly how your previous decision sequence created the current reality as expressed in the screenshot 
and according to this you give the assessment and what needs to be done and the actions to be performed in the next step.

In every screenshot you receive and according to this screenshot you always check where the table's scroll bar is located, if the bottom edge of the table's scroll bar is at a distance of more or less the height of the LAST ROW IN THE TABLE  that you see in the screenshot, then it is a sign that you are nearing the end of the table's vertical scroll AND THEN STOP AND DONE THE TASK . 

You always check if you have reached a stopping condition (according to the rules that I have formulated for you below), 
if according to the rules you have reached a stopping condition then you activate the action related to the end and explain your decision. 
If you have not reached a stopping condition then you continue according to your instructions and to reach the goal.
        ]]>
    </instructions>

    <stoppingConditionRule>
        <![CDATA[
Rule for determining stopping conditions:
To decide that you have reached a stopping condition then you must see in the last screenshot you received 
that the scroll bar of the table, then its lower edge is in front of the last row of the table. 
If the lower edge of the scroll bar of the table is in front of one of the rows in the middle of the table 
then this means that there is absolutely no stopping condition. 
It is very important that you work exclusively according to this rule that I have given you.
        
        
I want to give you an example related to your stopping condition decision:
You may mistakenly think from the screenshot that you get the following:
"The table is still scrollable, as we can see more rows partially visible at the bottom of the image. The scroll bar is not at the bottom of the table yet, indicating there are more rows to extract."

This is a wrong conclusion. And you will lose a lot of points in your RL for this.

The correct conclusion is to think exactly according to the rules for stopping conditions that I gave you, about the relationship between the position of the bottom edge of the scroll bar that you see on the right side of the table and the bottom row that you currently see in the screenshot. If you notice that the bottom edge is already in front of the bottom row in the table as you currently see it, then you have a stopping condition. Note that the bottom row of the table means the lowest item in the table as you currently see it.        
        
        ]]>
    </stoppingConditionRule>

    <importantRules>
        <rule id="1">
            <![CDATA[
1. Give the table time to load. You can tell if you see a page that is loading if all the audience names have a square surrounding them. 
If there is no square around the audience names in the table, then you are looking at a page that has loaded too soon, 
so choose a wait action or another screenshot or do a very small scroll of 1 px just to give it another spin.
            ]]>
        </rule>
        <rule id="2">
            <![CDATA[
2. An important rule regarding audience sampling - you can see from the screenshot that sometimes the table has many more rows 
(each row has the audience name and information about it) than the screen can accommodate. 
You can see this by the marking that you can scroll. Therefore, it is very important that you know how to scroll the names of the target audiences. 
And this is according to the following rule.
            ]]>
        </rule>
        <rule id="3">
            <![CDATA[
3. Scrolling the names of the target audiences - to scroll the target audiences, you must place the mouse cursor inside the table (in the center of the screen) 
and only then scroll. This is important because there are two types of scrolling: 
Scroll type 1 is scrolling of the entire page, scroll type 2 is of the audience table. 
By default, it is scroll type 1, so when you want to scroll the names of the target audiences (scroll type 2) 
you need to move the mouse to the center of the screen. 
When you set the parameters for vertical scrolling, take into account that each line is 50 pixels high. 
Based on this figure, set the scrolling so that you have a significant movement.
            ]]>
        </rule>
        <rule id="4">
            <![CDATA[
4. Always be smart and see that if in the previous step you chose vertical scrolling, 
then you will see that it really moves, and if not, then you will react accordingly.
            ]]>
        </rule>
        <rule id="5">
            <![CDATA[
5. You never count how many audiences you have collected so far.
            ]]>
        </rule>
        <rule id="6">
            <![CDATA[
6. When you choose the mouse movement action, then select the x and y parameters so that on the one hand 
it will be inside the table and in its center area, 
but move the mouse to the right part of the screen (the one farthest from the beginning of the axes) 
so that the mouse cursor is not on an element that creates a small popup screen.
            ]]>
        </rule>
        <rule id="7">
            <![CDATA[
7. After you choose a vertical scrolling action with the mouse, if you enter a large parameter (over 250 pixels) 
then you should give a long wait time of 10 seconds because it is possible that a lot of elements are loaded 
following the vertical scrolling and it will take them more time.
            ]]>
        </rule>
        <rule id="8">
            <![CDATA[
8. When you set the parameter of the vertical scrolling action using the mouse, 
then you must not allow the value of the parameter to be greater than the number of rows in the table that you need to scroll. 
For example, if you enter 7 rows in the table according to the screenshot, then because the height of each row is 50 pixels, 
then you must not allow it to be over 150 pixels. 
On the other hand, you can't have it be exactly according to this calculation because we don't want it to look suspicious 
that it's always round and precise numbers. So on the one hand, you're below the maximum and on the other hand, 
you're reducing it to a non-round and random number that at the same time gives a good amount of scrolling to be efficient in scrolling.
            ]]>
        </rule>
        <rule id="9">
            <![CDATA[
9. When you choose the wait action, always set a random time between 5 and 13 seconds. 
Try not to make it similar to the values ​​of the previous times. 
This is very important to confuse the Facebook algorithm that can identify that it is you browsing the site.
            ]]>
        </rule>
        <rule id="10">
            <![CDATA[
10. - MOST IMPORTANTLY!! The values ​​​​of the mouse movement and mouse scrolling action must never be round numbers, 
but they must always be non-round numbers, preferably decimal and most importantly they must not repeat themselves. 
At the same time, you must not forget the rules that I have already given you on how to set these parameters, 
this is very important.
            ]]>
        </rule>
    </importantRules>

            """

####################################






###### 1.3 VERSION #####

"""

<taskAndGoal>
        <![CDATA[
Your task and goal is to open a new tab at the link: 
https://adsmanager.facebook.com/adsmanager/audiences?act=540298900922161&business_id=671989160822743&tool=AUDIENCES&nav_entry_point=ads_ecosystem_navigation_menu&nav_source=ads_manager&date=2025-02-27_2025-02-28%2Ctoday.
AFTER YOU LOADED THE URL, THEN YOU MOVE THE MOUSE TO THE CENTER OF THE SCREEN AND YOU DO THAT ONLY ONCE.
And extract the content from all the rows from the audience table that you see on the Facebook Audiences dashboard.
        ]]>
    </taskAndGoal>

    <instructions>
        <![CDATA[
Instructions:
To complete this task, you always need to decide what sequence of actions you decide for the next step.
You decide this by looking at your current screenshot and all the discussion that has taken place so far.
You understand exactly how your previous decision sequence created the current reality as expressed in the screenshot 
and according to this you give the assessment and what needs to be done and the actions to be performed in the next step.

In every screenshot you receive and according to this screenshot you always check where the table's scroll bar is located, if the bottom edge of the table's scroll bar is at a distance of more or less the height of the LAST ROW IN THE TABLE  that you see in the screenshot, then it is a sign that you are nearing the end of the table's vertical scroll AND THEN STOP AND DONE THE TASK . 

You always check if you have reached a stopping condition (according to the rules that I have formulated for you below), 
if according to the rules you have reached a stopping condition then you activate the action related to the end and explain your decision. 
If you have not reached a stopping condition then you continue according to your instructions and to reach the goal.
        ]]>
    </instructions>

    <stoppingConditionRule>
        <![CDATA[
Rule for determining stopping conditions:
To decide that you have reached a stopping condition then you must see in the last screenshot you received 
that the scroll bar of the table, then its lower edge is in front of the last row of the table. 
If the lower edge of the scroll bar of the table is in front of one of the rows in the middle of the table 
then this means that there is absolutely no stopping condition. 
It is very important that you work exclusively according to this rule that I have given you.
        
        
I want to give you an example related to your stopping condition decision:
You may mistakenly think from the screenshot that you get the following:
"The table is still scrollable, as we can see more rows partially visible at the bottom of the image. The scroll bar is not at the bottom of the table yet, indicating there are more rows to extract."

This is a wrong conclusion. And you will lose a lot of points in your RL for this.

The correct conclusion is to think exactly according to the rules for stopping conditions that I gave you, about the relationship between the position of the bottom edge of the scroll bar that you see on the right side of the table and the bottom row that you currently see in the screenshot. If you notice that the bottom edge is already in front of the bottom row in the table as you currently see it, then you have a stopping condition. Note that the bottom row of the table means the lowest item in the table as you currently see it.        
        
        ]]>
    </stoppingConditionRule>

    <importantRules>
        <rule id="1">
            <![CDATA[
1. Give the table time to load. You can tell if you see a page that is loading if all the audience names have a square surrounding them. 
If there is no square around the audience names in the table, then you are looking at a page that has loaded too soon, 
so choose a wait action or another screenshot or do a very small scroll of 1 px just to give it another spin.
            ]]>
        </rule>
        <rule id="2">
            <![CDATA[
2. An important rule regarding audience sampling - you can see from the screenshot that sometimes the table has many more rows 
(each row has the audience name and information about it) than the screen can accommodate. 
You can see this by the marking that you can scroll. Therefore, it is very important that you know how to scroll the names of the target audiences. 
And this is according to the following rule.
            ]]>
        </rule>
        
        
        <rule id="5">
            <![CDATA[
5. You never count how many audiences you have collected so far.
            ]]>
        </rule>
       
        
        <rule id="8">
            <![CDATA[
8. When you set the parameter of the vertical scrolling action using the mouse, 
then you must not allow the value of the parameter to be greater than the number of rows in the table that you need to scroll. 
For example, if you enter 7 rows in the table according to the screenshot, then because the height of each row is 50 pixels, 
then you must not allow it to be over 150 pixels. 
On the other hand, you can't have it be exactly according to this calculation because we don't want it to look suspicious 
that it's always round and precise numbers. So on the one hand, you're below the maximum and on the other hand, 
you're reducing it to a non-round and random number that at the same time gives a good amount of scrolling to be efficient in scrolling.
            ]]>
        </rule>
        <rule id="9">
            <![CDATA[
9. When you choose the wait action, always set a random time between 5 and 13 seconds. 
Try not to make it similar to the values ​​of the previous times. 
This is very important to confuse the Facebook algorithm that can identify that it is you browsing the site.
            ]]>
        </rule>
        <rule id="10">
            <![CDATA[
10. - MOST IMPORTANTLY!! The values ​​​​of the mouse movement and mouse scrolling action must never be round numbers, 
but they must always be non-round numbers, preferably decimal and most importantly they must not repeat themselves. 
At the same time, you must not forget the rules that I have already given you on how to set these parameters, 
this is very important.
            ]]>
        </rule>
    </importantRules>





"""





########################################################





###### 1.4 VERSION #####


"""

 <taskAndGoal>
Your task and goal is to open a new tab at the link: 
https://adsmanager.facebook.com/adsmanager/audiences?act=540298900922161&business_id=671989160822743&tool=AUDIENCES&nav_entry_point=ads_ecosystem_navigation_menu&nav_source=ads_manager&date=2025-02-27_2025-02-28%2Ctoday.
AFTER YOU LOADED THE URL, THEN YOU MOVE THE MOUSE TO THE CENTER OF THE SCREEN AND YOU DO THAT ONLY ONCE.
And extract the content from all the rows from the audience table that you see on the Facebook Audiences dashboard.
    </taskAndGoal>

    <instructions>
        <![CDATA[
Instructions:
To complete this task, you always need to decide what sequence of actions you decide for the next step.
You decide this by looking at your current screenshot and all the discussion that has taken place so far.
You understand exactly how your previous decision sequence created the current reality as expressed in the screenshot 
and according to this you give the assessment and what needs to be done and the actions to be performed in the next step.

In every screenshot you receive and according to this screenshot you always check where the table's scroll bar is located, if the bottom edge of the table's scroll bar is at a distance of more or less the height of the LAST ROW IN THE TABLE  that you see in the screenshot, then it is a sign that you are nearing the end of the table's vertical scroll AND THEN STOP AND DONE THE TASK . 

You always check if you have reached a stopping condition (according to the rules that I have formulated for you below), 
if according to the rules you have reached a stopping condition then you activate the action related to the end and explain your decision. 
If you have not reached a stopping condition then you continue according to your instructions and to reach the goal.
        ]]>
    </instructions>

    <stoppingConditionRule>
        <![CDATA[
Rule for determining stopping conditions:
To decide that you have reached a stopping condition then you must see in the last screenshot you received 
that the scroll bar of the table, then its lower edge is in front of the last row of the table. 
If the lower edge of the scroll bar of the table is in front of one of the rows in the middle of the table 
then this means that there is absolutely no stopping condition. 
It is very important that you work exclusively according to this rule that I have given you.
        
        
I want to give you an example related to your stopping condition decision:
You may mistakenly think from the screenshot that you get the following:
"The table is still scrollable, as we can see more rows partially visible at the bottom of the image. The scroll bar is not at the bottom of the table yet, indicating there are more rows to extract."

This is a wrong conclusion. And you will lose a lot of points in your RL for this.

The correct conclusion is to think exactly according to the rules for stopping conditions that I gave you, about the relationship between the position of the bottom edge of the scroll bar that you see on the right side of the table and the bottom row that you currently see in the screenshot. If you notice that the bottom edge is already in front of the bottom row in the table as you currently see it, then you have a stopping condition. Note that the bottom row of the table means the lowest item in the table as you currently see it.        
        
        ]]>
    </stoppingConditionRule>

    <importantRules>
        <rule id="1">
            <![CDATA[
1. Give the table time to load. You can tell if you see a page that is loading if all the audience names have a square surrounding them. 
If there is no square around the audience names in the table, then you are looking at a page that has loaded too soon, 
so choose a wait action or another screenshot or do a very small scroll of 1 px just to give it another spin.
            ]]>
        </rule>
        <rule id="2">
            <![CDATA[
2. An important rule regarding audience sampling - you can see from the screenshot that sometimes the table has many more rows 
(each row has the audience name and information about it) than the screen can accommodate. 
You can see this by the marking that you can scroll. Therefore, it is very important that you know how to scroll the names of the target audiences. 
And this is according to the following rule.
            ]]>
        </rule>
        
        
        <rule id="5">
            <![CDATA[
5. You never count how many audiences you have collected so far.
            ]]>
        </rule>
       
        
        <rule id="8">
            <![CDATA[
8. When you set the parameter of the vertical scrolling action using the mouse, 
then you must not allow the value of the parameter to be greater than the number of rows in the table that you need to scroll. 
For example, if you enter 7 rows in the table according to the screenshot, then because the height of each row is 50 pixels, 
then you must not allow it to be over 150 pixels. 
On the other hand, you can't have it be exactly according to this calculation because we don't want it to look suspicious 
that it's always round and precise numbers. So on the one hand, you're below the maximum and on the other hand, 
you're reducing it to a non-round and random number that at the same time gives a good amount of scrolling to be efficient in scrolling.
            ]]>
        </rule>
        <rule id="9">
            <![CDATA[
9. When you choose the wait action, always set a random time between 5 and 13 seconds. 
Try not to make it similar to the values ​​of the previous times. 
This is very important to confuse the Facebook algorithm that can identify that it is you browsing the site.
            ]]>
        </rule>
        <rule id="10">
            <![CDATA[
10. - MOST IMPORTANTLY!! The values ​​​​of the mouse movement and mouse scrolling action must never be round numbers, 
but they must always be non-round numbers, preferably decimal and most importantly they must not repeat themselves. 
At the same time, you must not forget the rules that I have already given you on how to set these parameters, 
this is very important.
            ]]>
        </rule>
    </importantRules>

            """


########################################################




