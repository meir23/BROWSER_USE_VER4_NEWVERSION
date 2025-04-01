<AdvancedCampaignEditingPage>

    <InformationLayer>
        <Condition>
            <URLStartsWith>https://adsmanager.facebook.com/adsmanager/manage/campaigns/edit/</URLStartsWith>
            <Layout>
                <Title>Campaign name</Title>
                <Title>Special ad categories</Title>
                <Title>Campaign details</Title>
                <Title>Budget</Title>
            </Layout>
        </Condition>
        <Description>
            If you see a layout in the middle of the screen containing any of the above titles, then you are on the "Advanced Campaign Editing Page." 
            Therefore, all content within the tag "InformationLayer" is relevant to your current decision. 
            
            This is critical because certain actions and decision-making processes must be followed when working within this specific editing interface.
            The campaign editing page is structured in a way that helps you modify, duplicate, or adjust campaign settings while ensuring consistency with platform best practices.

            when you are on a page where the URL starts with: https://adsmanager.facebook.com/adsmanager/manage/campaigns/edit/ if any popup window appears that covers the interface in the link, then you must prioritize the popup window and choose actions related to the popup window only.

        </Description>
    </InformationLayer>

    <ContextBetweenUnderstandingAndTask>
        <Description>
            Understanding that you are in the "Advanced Campaign Editing Page" is crucial because it has significant implications for selecting the correct action related to your assigned task. 
            This understanding dictates whether you should proceed with campaign duplication, modify existing settings, or refrain from making certain changes.
        </Description>
        <Rules>
            <Rule>
                <Task>Campaign Duplication Only</Task>
                <Action>
                    <ClickGreenButton>Publish</ClickGreenButton>
                    <Condition>
                        <Switch>
                            <Position>Left</Position>
                            <Status>Draft</Status>
                            <Note>
                                If the switch at the top right (near the three horizontal dots) is on the left, the campaign is in Draft mode.
                                You must leave it as is since the user may want to duplicate the campaign but not publish it yet.
                                This means that unless explicitly instructed otherwise, the duplicated campaign must remain in the same status as the original campaign.
                            </Note>
                        </Switch>
                    </Condition>
                </Action>
            </Rule>
            <Rule>
                <Task>Campaign Duplication with Parameter Changes</Task>
                <Action>
                    <EnterMode>Fine-Tune Duplication</EnterMode>
                    <IfTaskIsNotAllowed>
                        <ClosePage>
                            <ClickButton>X (Top Left)</ClickButton>
                            <Location>Near Meta Logo</Location>
                            <Note>
                                If your task requires campaign duplication but also specifies changes to parameters in the campaign, ad set, or ad, then you must not proceed with duplication immediately.
                                Instead, you need to exit the editing page by clicking the X button at the top left corner near the Meta logo.
                            </Note>
                        </ClosePage>
                    </IfTaskIsNotAllowed>
                </Action>
            </Rule>
        </Rules>
    </ContextBetweenUnderstandingAndTask>

    <SpatialNavigation>
        <NavigationMenu>
            <Indicator>Blue Square</Indicator>
            <Description>
                The navigation menu at the top middle of the screen helps you identify your current location within the campaign structure.
                This structure is presented as a hierarchical path that consists of:
                <Hierarchy>
                    <Level1>Campaign Name</Level1>
                    <Level2>Number of Ad Sets within the Campaign</Level2>
                    <Level3>Number of Ads within each Ad Set</Level3>
                </Hierarchy>
                
                The blue square highlights your current position in the campaign structure, giving you an indication of whether you are viewing the campaign level, ad set level, or individual ad level.
                This is important because certain actions can only be performed at specific levels of the hierarchy.
            </Description>
        </NavigationMenu>
    </SpatialNavigation>

    <Instructions>
        <Step>Confirm that you are indeed on a specific campaign editing page. If so, proceed to Step 2.</Step>
        <Step>
            If the task instructs you to duplicate the campaign without modifying any details, click the green "Publish" button at the bottom of the screen.
        </Step>
        <Step>
            If the task specifies that you need to make modifications to the campaign or its components (ad sets or ads), verify whether you are allowed to proceed. If modifications are required, but no explicit permission is given, exit the editing page.
        </Step>
    </Instructions>

    <DosAndDonts>
        <DoNot>
            <Rule>Do not change the campaign's status manually. If the switch at the top right is set to Draft mode, leave it as it is.</Rule>
            <Rule>Do not rename the duplicated campaign unless explicitly instructed to do so.</Rule>
            <Rule>Do not make any parameter changes unless specifically required by the task.</Rule>
        </DoNot>
        <Do>
            <Rule>If instructed, change the campaign name accordingly.</Rule>
            <Rule>Follow the instructions given within the task precisely and avoid making any assumptions regarding additional changes.</Rule>
            <Rule>Ensure that you are working at the correct hierarchy level before making any modifications.</Rule>
        </Do>
    </DosAndDonts>

</AdvancedCampaignEditingPage>