/*
Vincent Santos
Slop Fest Page, New Fest Modal, and Creating Slop Fests Tests
*/
import { test, expect } from '@playwright/test';
import { SlopFestPage } from '../pages/slopFestPage';

const URL = process.env.URL!
const gobbId = process.env.USER_4!;
const password = process.env.USER_4_PASS!
const festNameNoUser = "Fest No Invited Users"
const festNameNoUserTwo = "Another Fest With No Invited Users"
const festNameWithUser = "Fest With Users Invited"

test.describe('Slop Fest Page links tests', () => {

    /*
        Slop Fest Page: Links Test
        Checking if all side bar links are functioning properly while in the Slop Fest page
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/86
    */

    //From Slop Fest page navigate to Me Goblin page
    test('Should redirect to MeGoblin', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        let currentURL = await slopFestPage.getCurrentURL();
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigate to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Navigate to MeGoblin page
        await slopFestPage.goMeGoblin();
        //Validate if user is redirected to correct page
        currentURL = await slopFestPage.getCurrentURL();
        await expect(currentURL).toBe(URL + 'profile');     
        
    })

    //From Slop Fest Page, navigate to Recommend a slop page
    test('Should redirect to Recommend', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        let currentURL = await slopFestPage.getCurrentURL();
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigate to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Navigate to Recommend a slop page
        await slopFestPage.goRecommend();
        //Validate if user is redirected to correct page
        currentURL = await slopFestPage.getCurrentURL();
        await expect(currentURL).toBe(URL + 'profile/recommend');
    
    })

    //From Slop Fest Page, navigate to Settings page
    test('Should redirect to Settings', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        let currentURL = await slopFestPage.getCurrentURL();
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigate to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Navigate to Settings page
        await slopFestPage.goSettings();
        //Validate if user is redirected to correct page
        currentURL = await slopFestPage.getCurrentURL();
        await expect(currentURL).toBe(URL + 'profile/settings');
        
    })

    //From Slop Fest Page, log user out
    test('Should logout user', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        let currentURL = await slopFestPage.getCurrentURL();
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigate to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Logout user
        await slopFestPage.goLogout();
        //Validate if user is redirected to Homepage after logging out
        await page.waitForLoadState('networkidle');
        currentURL = await slopFestPage.getCurrentURL();
        await expect(currentURL).toBe(URL + '');
    })

    //From Slop Fest page, return to Home page
    test('Should redirect to Home page', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        let currentURL = await slopFestPage.getCurrentURL();
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Navigate to Home Page
        await slopFestPage.goHome();
        //Validate if user is redirected to Homepage after logging out
        await page.waitForLoadState('networkidle');
        currentURL = await slopFestPage.getCurrentURL();
        await expect(currentURL).toBe(URL + '');
        
    })

    /*
        Slop Fest Page: Default Page without any fests
        Checks if message "You have no fests" is displayed as default/when user has no fests
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/86
    */
    test('Should confirm default No Fest page', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigate to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Check default page
        await slopFestPage.noFest.isVisible();
        
    })


})


test.describe('New Fest Modal General Tests', () => {
    /*
    Slop Fest Page: New Fest Button is functioning when user has no fests
    Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/98
    */
    test('Should open New Fest Modal', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        await expect(slopFestPage.festModal).toBeVisible();
        

    })

    /*
    Layout Test: Checking if the New Fest Modal matches requirements and displays elements
    Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/98
    UI Validation Sheet: https://docs.google.com/spreadsheets/d/1OJOb7XA5phLI1HBTVIY4Ba9T8Y8sYNQJX5hP6NfWd7Y/edit?gid=1905451501#gid=1905451501
    */
    //Check if New Fest Modal Elements are present and functioning
    test('Modal should have elements present ', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        await expect(slopFestPage.festModal).toBeVisible();
        //Layout Test: Check if Name it label is present 
        await expect(slopFestPage.labelName).toBeVisible();
        //Layout Test: Check if Start Date label is present
        await expect(slopFestPage.labelStart).toBeVisible();
        /*  
        Functionality Test: Calendar pops up when Start Date field is clicked
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/105 
        */
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        //Layout Test: Check if End Date label is present
        await expect(slopFestPage.labelEnd).toBeVisible();
        /*  
        Functionality Test: Calendar pops up when End Date field is clicked
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/106 
        */
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        //Close calendar pop up
        await slopFestPage.festModal.click();
        //Layout Test: Check if Invitees label is present
        await expect(slopFestPage.labelGoblin).toBeVisible();
        /*  
        Functionality Test: List pops up when Choose Invitees arrow is clicked
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/122 
        */
        await slopFestPage.openInvitees();
        await expect(slopFestPage.inviteeSelectionList).toBeVisible();
        
    })
    /*  
        Functionality Test: Close Modal Button is working
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/122 
    */
    test('Should close the New Fest Modal', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        await expect(slopFestPage.festModal).toBeVisible();
        //Closing the Modal
        await slopFestPage.clickClose();
        await expect(slopFestPage.festModal).not.toBeVisible();
    })
    /*  
        Functionality Test: Closing the modal clears field contents
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/122 
    */
    test('Fields should be empty', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        await expect(slopFestPage.festModal).toBeVisible();
        //Fill up the fields
        //Entering the Fest Name
        await slopFestPage.enterFestName('Sample Name');
        //Entering Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectToday();
        //Entering the End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(5);
        //Closing the Modal
        await slopFestPage.clickClose();
        //Reopen the Modal
        await slopFestPage.newFestclick();
        //Check the fields
        await expect(slopFestPage.festName).toBeEmpty();
        await expect(slopFestPage.startDate).toBeEmpty();
        await expect(slopFestPage.endDate).toBeEmpty();
        

    })


})


test.describe('New Fest Modal Positive Tests', () => {

    //Fest Name Inputs
    /*  
        Positive Test: Single Character Input
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/103 
    */
    test('Should accept single character', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName('A');
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Entering Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectToday();
        //Entering the End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(5);
        //Check is the Fest On! button is active
        await expect(slopFestPage.festOn).toBeEnabled();
        //Close the modal
        await slopFestPage.clickClose();
    })
    /*  
        Positive Test: Multiple Character Input
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/107
    */
    test('Should accept multiple characters', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName('Sample Name');
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Entering Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectToday();
        //Entering the End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(5);
        //Check is the Fest On! button is active
        await expect(slopFestPage.festOn).toBeEnabled();
        //Close the modal
        await slopFestPage.clickClose();
    })
    /*  
        Positive Test: Numeric Characters
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/108
    */
    test('Should accept numeric characters', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName('123');
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Entering Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectToday();
        //Entering the End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(5);
        //Check is the Fest On! button is active
        await expect(slopFestPage.festOn).toBeEnabled();
        //Close the modal
        await slopFestPage.clickClose();
    })
    /*  
        Positive Test: Symbols
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/109
    */
    test('Should accept symbols', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName('!@#$%');
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Entering Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectToday();
        //Entering the End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(5);
        //Check is the Fest On! button is active
        await expect(slopFestPage.festOn).toBeEnabled();
        //Close the modal
        await slopFestPage.clickClose();
    })
    /*  
        Positive Test: Mixed Input
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/110
    */
    test('Should accept mixed inputs', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName('Fest on the 12th?!');
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Entering Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectToday();
        //Entering the End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(5);
        //Check is the Fest On! button is active
        await expect(slopFestPage.festOn).toBeEnabled();
        //Close the modal
        await slopFestPage.clickClose();
    })


    //Date inputs
    /*  
        Positive Test: Today's Date as Start date, future date as End Date
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/112
                   https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/118
    */
    //Today as the Start Date, and 5 Days after as End Date
    test('Should accept start - today, end - future', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName('Date Tests');
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Entering Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectToday();
        //Entering the End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(5);
        //Check is the Fest On! button is active
        await expect(slopFestPage.festOn).toBeEnabled();
        //Close the modal
        await slopFestPage.clickClose();
    })
    /*  
        Positive Test: Future Date as Start Date
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/113
    */
    //Future Date as the Start Date
    test('Should accept tomorrow as start date', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName('Date Tests');
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Entering Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(5);
        //Entering the End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(5);
        //Check is the Fest On! button is active
        await expect(slopFestPage.festOn).toBeEnabled();
        //Close the modal
        await slopFestPage.clickClose();
    })
    /*  
        Positive Test: Dates are the same
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/117
    */
    //Start and End dates are the same day
    test('Should accept same dates', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName('Date Tests');
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Entering Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(7);
        //Entering the End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(7);
        //Check is the Fest On! button is active
        await expect(slopFestPage.festOn).toBeEnabled();
        //Close the modal
        await slopFestPage.clickClose();
    })

    //Positive Test: Start is a month from now, and End date is in two
    test('Should accept dates months in the future', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName('Date Tests');
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Entering Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(30);
        //Entering the End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(30);
        //Check is the Fest On! button is active
        await expect(slopFestPage.festOn).toBeEnabled();
        //Close the modal
        await slopFestPage.clickClose();
    })
    /*  
        Positive Test: Changing the selected dates
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/114
                   https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/119
    */
    //Changing the selected date
    test('Should be able to change dates', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName('Date Tests');
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Entering Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(3);
        //Entering the End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(6);
        //Entering a new Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(4);
        //Entering a new End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(8);
        //Check is the Fest On! button is active
        await expect(slopFestPage.festOn).toBeEnabled();
        //Close the modal
        await slopFestPage.clickClose();
    })
})


test.describe('New Fest Modal Negative Tests', () => {

    /*  
        Negative Test: Skip the Fest Name Field
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/104
    */
    test('Skip Name Field', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(3);
        //Entering the End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(6);
        //Check is the Fest On! button is inactive
        await expect(slopFestPage.festOn).toBeDisabled();
        //Close the modal
        await slopFestPage.clickClose();

    })

    /*  
        Negative Test: Clear the Name Field
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/104
    */

    test('Clear field should trigger error', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName('To be cleared');
        //Unselect field
        await slopFestPage.festModal.click();
        //Clear the field
        await slopFestPage.enterFestName('');
        //Check for error message
        await expect(slopFestPage.nameError).toBeVisible();
    })

    /*  
        Negative Test: Start and End Dates are past dates
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/115
                   https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/120
    */
    //Today as the Start Date, and 5 Days after as End Date
    test('Should not accept past dates', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName('Date Tests');
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Entering Start Date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(-5);
        //Entering the End Date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(-3);
        //Check is the Fest On! button is active
        await expect(slopFestPage.festOn).toBeDisabled({ timeout: 2000 });
        //Close the modal
        await slopFestPage.clickClose();
    })

})

test.describe.serial('Creatings fests and checking Fest page changes', () => {
    /*  
        New Fest: Create a Fest with no invitees
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/131
    */
    test('Should create first fest', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName(festNameNoUser);
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Enter a valid start date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(2);
        //Enter a valid end date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(6);
        //Check is the Fest On! button is active
        await expect(slopFestPage.festOn).toBeEnabled({ timeout: 2000 });
        //Click submit
        await slopFestPage.submitFest();
        //Confirm if fest is created
        await expect(slopFestPage.festNumber1).toBeVisible();

    })

    test('Fest page header should change', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Check if heading is changed
        await expect(slopFestPage.withFests).toBeVisible();
    })
    /*  
        New Fest: New Fest feature functions the same even when user has active fests
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/101
    */
    test('Should create second fest', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName(festNameNoUserTwo);
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Enter a valid start date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(4);
        //Enter a valid end date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(8);
        //Check is the Fest On! button is active
        await expect(slopFestPage.festOn).toBeEnabled({ timeout: 2000 });
        //Click submit
        await slopFestPage.submitFest();
        //Confirm if fest is created
        await expect(slopFestPage.festNumber2).toBeVisible();
    })
    //Layout Test: Fests should be displayed according to layout
    test('Should have all active fests displayed', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Check if both fests are on page
        await expect(slopFestPage.withFests).toBeVisible();
        await expect(slopFestPage.festNumber2).toBeVisible();

    })
    //Functionality Test: Users are able to delete fests
    test('User is able to delete fests', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Open first fest
        await slopFestPage.openFest1();
        await page.waitForLoadState('networkidle');
        //Delete first fest
        await slopFestPage.deleteTheFests();
        //Open second fest
        await slopFestPage.openFest2();
        await page.waitForLoadState('networkidle');
        //Delete second fest
        await slopFestPage.deleteTheFests();
        //Confirm that the fests are deleted
        await expect(slopFestPage.withFests).not.toBeVisible();
        await expect(slopFestPage.festNumber2).not.toBeVisible();
        //Confirm that the header is back to default
        await expect(slopFestPage.noFest).toBeVisible();

    })
    /*  
        New Fest: Create a Fest with invitees (Active bug and should fail)
        Test Case: https://app.drivt.net/main/projects/6675bb9be3496d35963e0a27/testcases/131
    */
    test('Should create fest with invited users', async ({ page }) => {
        //Navigate to Webpage
        await page.goto('/')
        const slopFestPage = new SlopFestPage(page);
        //Login user using valid credentials from .env file
        await slopFestPage.loginUser(gobbId, password);
        await slopFestPage.checkProfileName();
        //Navigate to Profile homepage
        await slopFestPage.profileHome();
        //Navigating to the Slop Fest Page
        await slopFestPage.goSlopFest();
        //Opening the New Fest Modal
        await slopFestPage.newFestclick();
        //Entering the Fest Name
        await slopFestPage.enterFestName(festNameWithUser);
        //Check for error message
        await expect(slopFestPage.nameError).not.toBeVisible();
        //Enter a valid start date
        await slopFestPage.openStartDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(2);
        //Enter a valid end date
        await slopFestPage.openEndDate();
        await expect(slopFestPage.datePicker).toBeVisible();
        await slopFestPage.selectDate(6);
        //Open the attendees deop down menu
        await slopFestPage.openInvitees();
        //Select AutomateOne as an invite
        await slopFestPage.automateOne();
        //Select AutomateTwo as an invite
        await slopFestPage.automateTwo();
        //Check is the Fest On! button is active
        await slopFestPage.festBody.click(); //To close the list
        await expect(slopFestPage.festOn).toBeEnabled({ timeout: 2000 });
        //Click submit
        await slopFestPage.submitFest();
        //Confirm if fest is created
        await expect(slopFestPage.festBody).not.toBeVisible({ timeout: 5000 });
        await page.pause();
        await expect(slopFestPage.festNumber3).toBeVisible();

    })
})

