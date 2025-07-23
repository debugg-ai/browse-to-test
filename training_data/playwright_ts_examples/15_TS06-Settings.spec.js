
import { test, expect } from '@playwright/test';

// test.beforeEach(async ({ page }) => {
//     // Runs Uat

//     await page.goto('/login');
//     await page.locator('input[name="email"]').fill('kittisak.p@ginkgosoft.co.th');
//     await page.locator('input[name="password"]').fill('P@ssw0rd');
//     await page.getByRole('button', { name: 'Sign In', exact: true }).click();
//     // await page.getByRole('button', { name: 'Accept' }).click();
//     await page.locator('a').filter({ hasText: 'settings' }).click();
//     await page.waitForURL('/settings/configuration');
// });



test.beforeEach(async ({ page }) => {
    // Runs Dev

    await page.goto('/login');
    await page.locator('input[name="email"]').fill('test.gamekittisak@gmail.com');
    await page.locator('input[name="password"]').fill('ZXcv.!2345');
    await page.getByRole('button', { name: 'Sign In', exact: true }).click();
    // await page.getByRole('button', { name: 'Accept' }).click();
    await page.locator('a').filter({ hasText: 'settings' }).click();
    await page.waitForURL('/settings/configuration');
});




test('TC01 Show Settings ', async ({ page }) => {

    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC01 Show Settings/01.Default Page.png', fullPage: true });

});



test('TC02 Chang Batch Size ', async ({ page }) => {
    await page.getByRole('link', { name: 'Configuration' }).click();
    await page.getByRole('tab', { name: 'System Configuration' }).click();
    await page.waitForTimeout(1000);
    await page.getByRole('textbox').fill('2222');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC02 Chang Batch Size /01.2222.png', fullPage: true });
    await page.waitForTimeout(1000);
    await page.getByRole('textbox').fill('10');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC02 Chang Batch Size /02.10.png', fullPage: true });
    await page.getByRole('textbox').fill('30303');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC02 Chang Batch Size /03.30303.png', fullPage: true });

});




test('TC03 Check Status Interval Filing ', async ({ page }) => {
    await page.getByRole('link', { name: 'Configuration' }).click();
    await page.getByRole('tab', { name: 'System Configuration' }).click();
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/01.Default Page.png', fullPage: true });
    await page.locator('div').filter({ hasText: /^Check Filing Status Frequency \(Hour\)6$/ }).nth(2).click();
    await page.getByRole('option', { name: '1', exact: true }).click();
    await page.locator('div').filter({ hasText: /^Check Filing Status Frequency \(Hour\)1$/ }).nth(2).click();
    await page.getByRole('option', { name: '2', exact: true }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/02.Check Filing 2.png', fullPage: true });
    await page.locator('div').filter({ hasText: /^Check Filing Status Frequency \(Hour\)2$/ }).nth(2).click();
    await page.getByText('3', { exact: true }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/03.Check Filing 3.png', fullPage: true });
    await page.locator('div').filter({ hasText: /^Check Filing Status Frequency \(Hour\)3$/ }).nth(2).click();
    await page.getByRole('option', { name: '4', exact: true }).locator('span').click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/04.Check Filing 4.png', fullPage: true });
    await page.locator('div').filter({ hasText: /^Check Filing Status Frequency \(Hour\)4$/ }).nth(2).click();
    await page.getByRole('option', { name: '6' }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/05.Check Filing 6.png', fullPage: true });
    await page.locator('div').filter({ hasText: /^Check Filing Status Frequency \(Hour\)6$/ }).nth(2).click();
    await page.getByRole('option', { name: '12' }).locator('span').click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/06.Check Filing 12.png', fullPage: true });
    await page.locator('div').filter({ hasText: /^Check Filing Status Frequency \(Hour\)12$/ }).nth(2).click();
    await page.getByRole('option', { name: '24' }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/07.Check Filing 24.png', fullPage: true });


});




test('TC03 Check Status Interval Payment  ', async ({ page }) => {
    await page.getByRole('link', { name: 'Configuration' }).click();
    await page.getByRole('tab', { name: 'System Configuration' }).click();
    await page.locator('div').filter({ hasText: /^Check Payment Frequency \(Hour\)6$/ }).nth(2).click();
    await page.getByRole('option', { name: '1', exact: true }).locator('span').click();
    await page.locator('div').filter({ hasText: /^Check Payment Frequency \(Hour\)1$/ }).nth(2).click();
    await page.getByRole('option', { name: '2', exact: true }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/08.Check Payment  2.png', fullPage: true });
    await page.locator('div').filter({ hasText: /^Check Payment Frequency \(Hour\)2$/ }).nth(2).click();
    await page.getByText('3', { exact: true }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/09.Check Payment  3.png', fullPage: true });
    await page.locator('div').filter({ hasText: /^Check Payment Frequency \(Hour\)3$/ }).nth(2).click();
    await page.getByRole('option', { name: '4', exact: true }).locator('span').click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/10.Check Payment  4.png', fullPage: true });
    await page.locator('div').filter({ hasText: /^Check Payment Frequency \(Hour\)4$/ }).nth(2).click();
    await page.getByRole('option', { name: '6' }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/11.Check Payment  6.png', fullPage: true });
    await page.locator('div').filter({ hasText: /^Check Payment Frequency \(Hour\)6$/ }).nth(2).click();
    await page.getByRole('option', { name: '12' }).locator('span').click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/12.Check Payment  12.png', fullPage: true });
    await page.locator('div').filter({ hasText: /^Check Payment Frequency \(Hour\)12$/ }).nth(2).click();
    await page.getByRole('option', { name: '24' }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/13.Check Payment  24.png', fullPage: true });


});



test('TC03 Check Status Interval  ', async ({ page }) => {
    await page.getByRole('link', { name: 'Configuration' }).click();
    await page.getByRole('tab', { name: 'System Configuration' }).click();
    await page.locator('div').filter({ hasText: /^Check Filing Status Frequency \(Hour\)6$/ }).nth(2).click();
    await page.getByRole('option', { name: '12' }).locator('span').click();
    await page.locator('div').filter({ hasText: /^Check Payment Frequency \(Hour\)6$/ }).nth(2).click();
    await page.getByRole('option', { name: '24' }).first().click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC03 Check Status Interval/14.Check All.png', fullPage: true });


});


















test('TC04 Application  ', async ({ page }) => {

    await page.getByRole('tab', { name: 'Application' }).click();
    await page.waitForTimeout(500);
    await expect.soft(page.getByRole('heading', { name: 'Hamburger Menu' })).toBeVisible();
    await expect.soft(page.getByText('Configuration for display hamburger menu')).toBeVisible();
    await expect.soft(page.locator('div').filter({ hasText: /^zDOX:$/ })).toBeVisible();
    await expect.soft(page.getByText('getInvoice:')).toBeVisible();
    await expect.soft(page.getByRole('heading', { name: 'Security' })).toBeVisible();
    await expect.soft(page.getByText('Security Configuration')).toBeVisible();
    await expect.soft(page.getByText('Min Password Age:')).toBeVisible();
    await expect.soft(page.getByText('Max Password Age:')).toBeVisible();
    await expect.soft(page.getByRole('button', { name: 'Save' })).toBeVisible();
    await page.waitForTimeout(500);
    await expect.soft(page.getByRole('heading', { name: 'Hamburger Menu' })).toHaveText('Hamburger Menu');
    await expect.soft(page.getByText('Configuration for display hamburger menu')).toHaveText('Configuration for display hamburger menu');
    await expect.soft(page.locator('div').filter({ hasText: /^zDOX:$/ })).toHaveText('zDOX:');
    await expect.soft(page.getByText('getInvoice:')).toHaveText('getInvoice:');
    await expect.soft(page.getByRole('heading', { name: 'Security' })).toHaveText('Security');
    await expect.soft(page.getByText('Security Configuration')).toHaveText('Security Configuration');
    await expect.soft(page.getByText('Min Password Age:')).toHaveText('Min Password Age:');
    await expect.soft(page.getByText('Max Password Age:')).toHaveText('Max Password Age:');
    await expect.soft(page.getByRole('button', { name: 'Save' })).toHaveText('Save');
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC04 Application/01.Default Page.png' });





});

test('TC04 Password age policy settings ', async ({ page }) => {

    await page.waitForTimeout(1000);
    await page.getByRole('tab', { name: 'Application' }).click();
    await page.waitForTimeout(1000);
    await expect(page.getByRole('heading', { name: 'Security' })).toHaveText('Security');
    await expect(page.getByText('Security Configuration')).toHaveText('Security Configuration');
    await expect(page.getByText('Max Password Age:')).toHaveText('Max Password Age:');
    await expect(page.getByText('Min Password Age:')).toHaveText('Min Password Age:');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC04 Application/02. Password age policy details.png' });



});



test('TC05 Mail Server  ', async ({ page }) => {

    await page.getByRole('tab', { name: 'Mail Server' }).locator('span').nth(1).click();
    await page.getByRole('tab', { name: 'Mail Server' }).locator('span').nth(1).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC05 Mail Server/01.Default Page.png' });

});


test('TC05 Add Mail Server  ', async ({ page }) => {
    await page.getByRole('tab', { name: 'Mail Server' }).locator('span').nth(1).click();
    await page.getByRole('tab', { name: 'Mail Server' }).locator('span').nth(1).click();
    await page.waitForTimeout(1500);
    await page.getByRole('button', { name: 'Add' }).click();
    await page.waitForTimeout(500);
    await page.locator('input[name="serverDescription"]').fill('Automate Test');
    await page.getByRole('combobox').selectOption('SMTP');
    await page.locator('input[name="serverName"]').fill('Automate_Test@gmail.com');
    await page.locator('input[name="serverPort"]').fill('1234');
    await page.locator('input[name="serverUser"]').fill('AT');
    await page.locator('input[name="serverPassword"]').fill('ASD123!@#zxc');
    await page.locator('input[name="senderAddress"]').fill('Automate_Test@gmail.com');
    await page.locator('input[name="senderName"]').fill('Auto Test');
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC05 Mail Server/02.Add Mail Server.png' });
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: 'Cancel' }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC05 Mail Server/03.Click Cancel.png' });
    await page.waitForTimeout(1500);
    await page.getByRole('button', { name: 'Add' }).click();
    await page.waitForTimeout(500);
    await page.locator('input[name="serverDescription"]').fill('Automate Test');
    await page.getByRole('combobox').selectOption('SMTP');
    await page.locator('input[name="serverName"]').fill('Automate_Test@gmail.com');
    await page.locator('input[name="serverPort"]').fill('1234');
    await page.locator('input[name="serverUser"]').fill('AT');
    await page.locator('input[name="serverPassword"]').fill('ASD123!@#zxc');
    await page.locator('input[name="senderAddress"]').fill('Automate_Test@gmail.com');
    await page.locator('input[name="senderName"]').fill('Auto Test');
    await page.waitForTimeout(1500);
    await page.getByRole('button', { name: 'Save' }).click();
    await page.waitForTimeout(500);
    await expect.soft(page.getByRole('cell', { name: 'Automate Test' })).toBeVisible();
    await expect.soft(page.getByRole('cell', { name: 'Automate Test' })).toHaveText('Automate Test');
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC05 Mail Server/04.Click Save.png' });
    await page.waitForTimeout(500);


});





test('TC05 Edit Mail Server  ', async ({ page }) => {

    await page.getByRole('tab', { name: 'Mail Server' }).locator('span').nth(1).click();
    await page.getByRole('tab', { name: 'Mail Server' }).locator('span').nth(1).click();
    await page.waitForTimeout(500);
    await page.getByRole('row', { name: 'Automate Test Automate_Test@' }).getByRole('button').nth(1).click();
    await page.waitForTimeout(500);
    await page.locator('input[name="serverDescription"]').fill('Edit Auto');
    await page.getByRole('combobox').selectOption('API');
    await page.locator('input[name="serverName"]').fill('Edit_Automate_Test@gmail.com');
    await page.locator('input[name="serverPort"]').fill('4321');
    await page.locator('input[name="serverUser"]').fill('TA');
    await page.locator('input[name="serverPassword"]').fill('cxz#@!321DSA');
    await page.locator('input[name="senderAddress"]').fill('Edit_Automate_Test@gmail.com');
    await page.locator('input[name="senderName"]').fill('Test Auto');
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC05 Mail Server/05.Edit Details.png' });
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: 'Cancel' }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC05 Mail Server/06.Edit Click Cancel.png' });
    await page.waitForTimeout(1500);
    await page.getByRole('row', { name: 'Automate Test Automate_Test@' }).getByRole('button').nth(1).click();
    await page.waitForTimeout(500);
    await page.locator('input[name="serverDescription"]').fill('Edit Auto');
    await page.getByRole('combobox').selectOption('API');
    await page.locator('input[name="serverName"]').fill('Edit_Automate_Test@gmail.com');
    await page.locator('input[name="serverPort"]').fill('4321');
    await page.locator('input[name="serverUser"]').fill('TA');
    await page.locator('input[name="serverPassword"]').fill('cxz#@!321DSA');
    await page.locator('input[name="senderAddress"]').fill('Edit_Automate_Test@gmail.com');
    await page.locator('input[name="senderName"]').fill('Test Auto');
    await page.waitForTimeout(1500);
    await page.getByRole('button', { name: 'Save' }).click();
    await page.waitForTimeout(500);
    await expect.soft(page.getByRole('cell', { name: 'Edit Auto' })).toBeVisible();
    await expect.soft(page.getByRole('cell', { name: 'Edit Auto' })).toHaveText('Edit Auto');
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC05 Mail Server/07.Edit Click Save.png' });
    await page.waitForTimeout(500);

});



test('TC05 Delete Mail Server  ', async ({ page }) => {

    await page.getByRole('tab', { name: 'Mail Server' }).locator('span').nth(1).click();
    await page.getByRole('tab', { name: 'Mail Server' }).locator('span').nth(1).click();
    await page.waitForTimeout(500);
    await page.getByRole('row', { name: 'Edit Auto Edit_Automate_Test@' }).getByRole('button').nth(2).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC05 Mail Server/08.Delete Cancel.png' });
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: 'Cancel' }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC05 Mail Server/09.Delete Click Cancel.png' });
    await page.waitForTimeout(500);
    await page.getByRole('row', { name: 'Edit Auto Edit_Automate_Test@' }).getByRole('button').nth(2).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC05 Mail Server/10.Delete Confirm.png' });
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: 'Confirm' }).click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC05 Mail Server/11.Delete Click Confirm.png' });
    await page.waitForTimeout(500);




});





test('TC06 Permission  ', async ({ page }) => {
    await page.getByRole('link', { name: 'Permission' }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC06 Permission/01.Default Page.png' });

});



test('TC07 Organization  ', async ({ page }) => {
    await page.getByRole('link', { name: 'Organization' }).click();
    // await page.locator('#mat-tab-label-0-4').click();
    // await page.locator('#mat-tab-label-2-0').click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC07 Organization/01.Default Page.png' });
    await page.getByRole('tab', { name: 'Company' }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC07 Organization/02.Company.png' });
    await page.getByRole('tab', { name: 'Users' }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC07 Organization/03.User.png' });

});













test('TC08 Creation Organization General Information ', async ({ page }) => {
    await page.getByRole('link', { name: 'Organization' }).click();
    await page.getByRole('button', { name: 'Add' }).click();
    await page.waitForTimeout(500);
    await page.waitForTimeout(500);
    await expect.soft(page.locator('div').filter({ hasText: 'General InformationOrganization Name English*Organization Name Thai*' }).nth(3)).toBeVisible();
    await page.waitForTimeout(500);
    await page.locator('input[name="nameEng"]').click();
    await page.locator('input[name="nameTha"]').click();
    await page.locator('input[name="orgAbbr"]').click();
    await page.locator('input[name="nameEng"]').click();
    await page.waitForTimeout(500);
    await expect.soft(page.getByText('Organization Name English is required')).toHaveText('Organization Name English is required');
    await page.waitForTimeout(500);
    await expect.soft(page.getByText('Organization Name Thai is required')).toHaveText('Organization Name Thai is required');
    await page.waitForTimeout(500);
    await expect.soft(page.getByText('Organization Abbreviation is required')).toHaveText('Organization Abbreviation is required');
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/01. Creation/01. General Information Required.png' });
    await page.locator('input[name="nameEng"]').fill('Automate Test');
    await page.locator('input[name="nameTha"]').fill('ทดสอบอัตโนมัติ');
    await page.locator('input[name="orgAbbr"]').fill('AT');
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/01. Creation/02. Input General Information.png' });

});





test('TC08 Creation Organization ', async ({ page }) => {
    await page.getByRole('link', { name: 'Organization' }).click();
    await page.getByRole('button', { name: 'Add' }).click();
    await page.waitForTimeout(500);
    await expect.soft(page.locator('div').filter({ hasText: 'General InformationOrganization Name English*Organization Name Thai*' }).nth(3)).toBeVisible();
    await page.waitForTimeout(500);
    await page.locator('input[name="nameEng"]').fill('Automate Test');
    await page.locator('input[name="nameTha"]').fill('ทดสอบอัตโนมัติ');
    await page.locator('input[name="orgAbbr"]').fill('AT');
    await page.getByRole('button', { name: 'Save' }).click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/01. Creation/03. Creation Organization.png' });
    await page.waitForTimeout(1500);


});





test('TC08 Edit Watcher Server File  ', async ({ page }) => {
    await page.getByRole('link', { name: 'Organization' }).click();
    await page.getByRole('row', { name: 'Automate Test ทดสอบอัตโนมัติ' }).getByRole('button').first().click();
    await page.waitForTimeout(500);
    await page.getByRole('tab', { name: 'Watcher' }).click();
    await page.waitForTimeout(500);
    await expect.soft(page.locator('div').filter({ hasText: 'General InformationWatcherResponse FileExport ReceiptsEnable WatcherCancelSave' }).nth(3)).toBeVisible();
    await page.waitForTimeout(500);
    await page.getByLabel('Enable Watcher').click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/02. Edit Watcher/01. Watcher Details.png' });
    await page.waitForTimeout(1000);
    await page.locator('label').filter({ hasText: 'Path info' }).locator('mat-icon').click();
    await page.waitForTimeout(500);
    await expect.soft(page.getByRole('heading', { name: 'Naming Convention' })).toHaveText('Naming Convention');
    await expect.soft(page.getByText('Place symbols inside the bracket { } ex. File_{yyyyMMdd}')).toHaveText('Place symbols inside the bracket { } ex. File_{yyyyMMdd}');
    await expect.soft(page.getByRole('cell', { name: 'Symbol' })).toHaveText('Symbol');
    await expect.soft(page.getByRole('cell', { name: 'Description' })).toHaveText('Description');
    await expect.soft(page.getByRole('cell', { name: 'Examples' })).toHaveText('Examples');
    await expect.soft(page.getByRole('cell', { name: 'companyTaxId' })).toHaveText('companyTaxId');
    await expect.soft(page.getByRole('cell', { name: 'Company Tax ID as a 13-digit' })).toHaveText('Company Tax ID as a 13-digit');
    await expect.soft(page.getByRole('cell', { name: '1234567890123' })).toHaveText('1234567890123');
    await expect.soft(page.getByRole('cell', { name: 'companyAbbr' })).toHaveText('companyAbbr');
    await expect.soft(page.getByRole('cell', { name: 'Company Abbreviation' })).toHaveText('Company Abbreviation');
    await expect.soft(page.getByRole('cell', { name: 'ABC, GKS,...' })).toHaveText('ABC, GKS,...');
    await expect.soft(page.getByRole('cell', { name: 'group', exact: true })).toHaveText('group');
    await expect.soft(page.getByRole('cell', { name: 'The name of group user' })).toHaveText('The name of group user');
    await expect.soft(page.getByRole('cell', { name: 'Default' })).toHaveText('Default');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/02. Edit Watcher/02. Path Convention.png' });
    await page.waitForTimeout(1000);
    await page.getByRole('dialog').press('Escape');
    await page.waitForTimeout(1000);
    await page.getByLabel('Select Server SFTPzDOX').selectOption('SFTP');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/02. Edit Watcher/03. Watcher SFTP.png' });
    await page.waitForTimeout(1000);
    await page.getByLabel('Select Server SFTPzDOX').selectOption('zDOX');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/02. Edit Watcher/04. Watcher zDOX Details.png' });
    await page.waitForTimeout(1000);
    await page.getByRole('button', { name: 'Cancel' }).click();


});






test('TC08 Edit Organization Response Files ', async ({ page }) => {
    await page.getByRole('link', { name: 'Organization' }).click();
    await page.getByRole('row', { name: 'Automate Test ทดสอบอัตโนมัติ' }).getByRole('button').first().click();
    await page.waitForTimeout(500);
    await page.getByRole('tab', { name: 'Response File' }).click();
    await page.waitForTimeout(500);
    await expect.soft(page.locator('div').filter({ hasText: 'General InformationWatcherResponse FileExport ReceiptsEnable Create Response' }).nth(3)).toBeVisible();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/03. Edit Response Files/01. Response Files.png' });
    await page.getByLabel('Enable Create Response File').click();
    await page.waitForTimeout(1000);
    await page.locator('label').filter({ hasText: 'Path info' }).locator('mat-icon').click();

    await expect.soft(page.getByRole('heading', { name: 'Naming Convention' })).toHaveText('Naming Convention');
    await expect.soft(page.getByText('Place symbols inside the bracket { } ex. File_{yyyyMMdd}')).toHaveText('Place symbols inside the bracket { } ex. File_{yyyyMMdd}');
    await expect.soft(page.getByRole('cell', { name: 'Symbol' })).toHaveText('Symbol');
    await expect.soft(page.getByRole('cell', { name: 'Description' })).toHaveText('Description');
    await expect.soft(page.getByRole('cell', { name: 'Examples' })).toHaveText('Examples');
    await expect.soft(page.getByRole('cell', { name: 'companyTaxId' })).toHaveText('companyTaxId');
    await expect.soft(page.getByRole('cell', { name: 'Company Tax ID as a 13-digit' })).toHaveText('Company Tax ID as a 13-digit');
    await expect.soft(page.getByRole('cell', { name: '1234567890123' })).toHaveText('1234567890123');
    await expect.soft(page.getByRole('cell', { name: 'companyAbbr' })).toHaveText('companyAbbr');
    await expect.soft(page.getByRole('cell', { name: 'Company Abbreviation' })).toHaveText('Company Abbreviation');
    await expect.soft(page.getByRole('cell', { name: 'ABC, GKS,...' })).toHaveText('ABC, GKS,...');
    await expect.soft(page.getByRole('cell', { name: 'group', exact: true })).toHaveText('group');
    await expect.soft(page.getByRole('cell', { name: 'The name of group user' })).toHaveText('The name of group user');
    await expect.soft(page.getByRole('cell', { name: 'Default' })).toHaveText('Default');
    await expect.soft(page.getByRole('cell', { name: 'typeCode' })).toHaveText('typeCode');
    await expect.soft(page.getByRole('cell', { name: 'The type code of instrument' })).toHaveText('The type code of instrument');
    await expect.soft(page.getByRole('cell', { name: '1,2,3,4,...' })).toHaveText('1,2,3,4,...');
    await expect.soft(page.getByRole('cell', { name: 'upload:', exact: true })).toHaveText('upload:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use upload date' })).toHaveText('A prefix to use upload date');
    await expect.soft(page.getByRole('cell', { name: 'upload:yyyyMMdd-HHmmssSSS -> 20241231-014530617' })).toHaveText('upload:yyyyMMdd-HHmmssSSS -> 20241231-014530617');
    await expect.soft(page.getByRole('cell', { name: 'submit:', exact: true })).toHaveText('submit:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use submit date' })).toHaveText('A prefix to use submit date');
    await expect.soft(page.getByRole('cell', { name: 'submit:yyyyMMdd-HHmmssSSS -> 20241231-014530617' })).toHaveText('submit:yyyyMMdd-HHmmssSSS -> 20241231-014530617');
    await expect.soft(page.getByRole('cell', { name: 'payment:', exact: true })).toHaveText('payment:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use payment date' })).toHaveText('A prefix to use payment date');
    await expect.soft(page.getByRole('cell', { name: 'payment:yyyyMMdd-HHmmssSSS -> 20241231-014530617' })).toHaveText('payment:yyyyMMdd-HHmmssSSS -> 20241231-014530617');
    await expect.soft(page.getByRole('cell', { name: 'yyyy', exact: true })).toHaveText('yyyy');
    await expect.soft(page.getByRole('cell', { name: 'Year as a four-digit Number' })).toHaveText('Year as a four-digit Number');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 2024' })).toHaveText('2024-12-31 -> 2024');
    await expect.soft(page.getByRole('cell', { name: 'yy', exact: true })).toHaveText('yy');
    await expect.soft(page.getByRole('cell', { name: 'Year , from 00 to 99' })).toHaveText('Year , from 00 to 99');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 24' })).toHaveText('2024-12-31 -> 24');
    await expect.soft(page.getByRole('cell', { name: 'MM', exact: true })).toHaveText('MM');
    await expect.soft(page.getByRole('cell', { name: 'Month, from 01 through 12' })).toHaveText('Month, from 01 through 12');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 12' })).toHaveText('2024-12-31 -> 12');
    await expect.soft(page.getByRole('cell', { name: 'dd', exact: true })).toHaveText('dd');
    await expect.soft(page.getByRole('cell', { name: 'Day, from 01 through 31' })).toHaveText('Day, from 01 through 31');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 31' })).toHaveText('2024-12-31 -> 31');
    await expect.soft(page.getByRole('cell', { name: 'HH', exact: true })).toHaveText('HH');
    await expect.soft(page.getByRole('cell', { name: 'The hour, using a 24-hour clock from 00 to 23' })).toHaveText('The hour, using a 24-hour clock from 00 to 23');
    await expect.soft(page.getByRole('cell', { name: '01:45:30 -> 01' })).toHaveText('01:45:30 -> 01');
    await expect.soft(page.getByRole('cell', { name: 'mm', exact: true })).toHaveText('mm');
    await expect.soft(page.getByRole('cell', { name: 'The minute, from 00 through 59' })).toHaveText('The minute, from 00 through 59');
    await expect.soft(page.getByRole('cell', { name: '01:45:30 -> 45' })).toHaveText('01:45:30 -> 45');
    await expect.soft(page.getByRole('cell', { name: 'ss', exact: true })).toHaveText('ss');
    await expect.soft(page.getByRole('cell', { name: 'The second, from 00 through 59' })).toHaveText('The second, from 00 through 59');
    await expect.soft(page.getByRole('cell', { name: '01:45:30 -> 30' })).toHaveText('01:45:30 -> 30');
    await expect.soft(page.getByRole('cell', { name: 'SSS', exact: true })).toHaveText('SSS');
    await expect.soft(page.getByRole('cell', { name: 'The milliseconds in a date and time value' })).toHaveText('The milliseconds in a date and time value');
    await expect.soft(page.getByRole('cell', { name: '01:45:30.617 -> 617' })).toHaveText('01:45:30.617 -> 617');



    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/03. Edit Response Files/02. Path Convention.png' });
    await page.waitForTimeout(1000);
    await page.getByRole('dialog').press('Escape');
    await page.locator('label').filter({ hasText: 'File Name info' }).locator('mat-icon').click();
    await page.waitForTimeout(500);

    await expect.soft(page.getByRole('heading', { name: 'Naming Convention' })).toHaveText('Naming Convention');
    await expect.soft(page.getByText('Place symbols inside the bracket { } ex. File_{yyyyMMdd}')).toHaveText('Place symbols inside the bracket { } ex. File_{yyyyMMdd}');
    await expect.soft(page.getByRole('cell', { name: 'Symbol' })).toHaveText('Symbol');
    await expect.soft(page.getByRole('cell', { name: 'Description' })).toHaveText('Description');
    await expect.soft(page.getByRole('cell', { name: 'Examples' })).toHaveText('Examples');
    await expect.soft(page.getByRole('cell', { name: 'companyTaxId' })).toHaveText('companyTaxId');
    await expect.soft(page.getByRole('cell', { name: 'Company Tax ID as a 13-digit' })).toHaveText('Company Tax ID as a 13-digit');
    await expect.soft(page.getByRole('cell', { name: '1234567890123' })).toHaveText('1234567890123');
    await expect.soft(page.getByRole('cell', { name: 'companyAbbr' })).toHaveText('companyAbbr');
    await expect.soft(page.getByRole('cell', { name: 'Company Abbreviation' })).toHaveText('Company Abbreviation');
    await expect.soft(page.getByRole('cell', { name: 'ABC, GKS,...' })).toHaveText('ABC, GKS,...');
    await expect.soft(page.getByRole('cell', { name: 'group', exact: true })).toHaveText('group');
    await expect.soft(page.getByRole('cell', { name: 'The name of group user' })).toHaveText('The name of group user');
    await expect.soft(page.getByRole('cell', { name: 'Default' })).toHaveText('Default');
    await expect.soft(page.getByRole('cell', { name: 'typeCode' })).toHaveText('typeCode');
    await expect.soft(page.getByRole('cell', { name: 'The type code of instrument' })).toHaveText('The type code of instrument');
    await expect.soft(page.getByRole('cell', { name: '1,2,3,4,...' })).toHaveText('1,2,3,4,...');
    await expect.soft(page.getByRole('cell', { name: 'upload:', exact: true })).toHaveText('upload:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use upload date' })).toHaveText('A prefix to use upload date');
    await expect.soft(page.getByRole('cell', { name: 'upload:yyyyMMdd-HHmmssSSS -> 20241231-014530617' })).toHaveText('upload:yyyyMMdd-HHmmssSSS -> 20241231-014530617');
    await expect.soft(page.getByRole('cell', { name: 'submit:', exact: true })).toHaveText('submit:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use submit date' })).toHaveText('A prefix to use submit date');
    await expect.soft(page.getByRole('cell', { name: 'submit:yyyyMMdd-HHmmssSSS -> 20241231-014530617' })).toHaveText('submit:yyyyMMdd-HHmmssSSS -> 20241231-014530617');
    await expect.soft(page.getByRole('cell', { name: 'payment:', exact: true })).toHaveText('payment:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use payment date' })).toHaveText('A prefix to use payment date');
    await expect.soft(page.getByRole('cell', { name: 'payment:yyyyMMdd-HHmmssSSS -> 20241231-014530617' })).toHaveText('payment:yyyyMMdd-HHmmssSSS -> 20241231-014530617');
    await expect.soft(page.getByRole('cell', { name: 'yyyy', exact: true })).toHaveText('yyyy');
    await expect.soft(page.getByRole('cell', { name: 'Year as a four-digit Number' })).toHaveText('Year as a four-digit Number');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 2024' })).toHaveText('2024-12-31 -> 2024');
    await expect.soft(page.getByRole('cell', { name: 'yy', exact: true })).toHaveText('yy');
    await expect.soft(page.getByRole('cell', { name: 'Year , from 00 to 99' })).toHaveText('Year , from 00 to 99');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 24' })).toHaveText('2024-12-31 -> 24');
    await expect.soft(page.getByRole('cell', { name: 'MM', exact: true })).toHaveText('MM');
    await expect.soft(page.getByRole('cell', { name: 'Month, from 01 through 12' })).toHaveText('Month, from 01 through 12');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 12' })).toHaveText('2024-12-31 -> 12');
    await expect.soft(page.getByRole('cell', { name: 'dd', exact: true })).toHaveText('dd');
    await expect.soft(page.getByRole('cell', { name: 'Day, from 01 through 31' })).toHaveText('Day, from 01 through 31');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 31' })).toHaveText('2024-12-31 -> 31');
    await expect.soft(page.getByRole('cell', { name: 'HH', exact: true })).toHaveText('HH');
    await expect.soft(page.getByRole('cell', { name: 'The hour, using a 24-hour clock from 00 to 23' })).toHaveText('The hour, using a 24-hour clock from 00 to 23');
    await expect.soft(page.getByRole('cell', { name: '01:45:30 -> 01' })).toHaveText('01:45:30 -> 01');
    await expect.soft(page.getByRole('cell', { name: 'mm', exact: true })).toHaveText('mm');
    await expect.soft(page.getByRole('cell', { name: 'The minute, from 00 through 59' })).toHaveText('The minute, from 00 through 59');
    await expect.soft(page.getByRole('cell', { name: '01:45:30 -> 45' })).toHaveText('01:45:30 -> 45');
    await expect.soft(page.getByRole('cell', { name: 'ss', exact: true })).toHaveText('ss');
    await expect.soft(page.getByRole('cell', { name: 'The second, from 00 through 59' })).toHaveText('The second, from 00 through 59');
    await expect.soft(page.getByRole('cell', { name: '01:45:30 -> 30' })).toHaveText('01:45:30 -> 30');
    await expect.soft(page.getByRole('cell', { name: 'SSS', exact: true })).toHaveText('SSS');
    await expect.soft(page.getByRole('cell', { name: 'The milliseconds in a date and time value' })).toHaveText('The milliseconds in a date and time value');
    await expect.soft(page.getByRole('cell', { name: '01:45:30.617 -> 617' })).toHaveText('01:45:30.617 -> 617');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/03. Edit Response Files/03. File Name Convention.png' });
    await page.waitForTimeout(1000);
    await page.getByRole('dialog').press('Escape');
    await page.waitForTimeout(1000);
    await page.getByLabel('Select Server SFTPzDOX').selectOption('SFTP');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/03. Edit Response Files/04. Response SFTP.png' });
    await page.waitForTimeout(1000);
    await page.getByLabel('Select Server SFTPzDOX').selectOption('zDOX');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/03. Edit Response Files/05. Response zDOX Details.png' });
    await page.waitForTimeout(1000);
    await page.getByRole('button', { name: 'Cancel' }).click();


});





test('TC08 Edit Organization Export Receipts  ', async ({ page }) => {
    await page.getByRole('link', { name: 'Organization' }).click();
    await page.getByRole('row', { name: 'Automate Test ทดสอบอัตโนมัติ' }).getByRole('button').first().click();
    await page.waitForTimeout(500);
    await page.getByRole('tab', { name: 'Export Receipts' }).click();
    await page.waitForTimeout(500);
    await expect.soft(page.locator('div').filter({ hasText: 'General InformationWatcherResponse FileExport ReceiptsEnable Export' }).nth(3)).toBeVisible();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/04. Edit Export Receipts/01. Export Receipts.png' });
    await page.getByLabel('Enable Export Receipts').click();
    await page.waitForTimeout(1000);
    await page.locator('label').filter({ hasText: 'Path info' }).locator('mat-icon').click();
    await expect.soft(page.getByRole('heading', { name: 'Naming Convention' })).toHaveText('Naming Convention');
    await expect.soft(page.getByText('Place symbols inside the bracket { } ex. File_{yyyyMMdd}')).toHaveText('Place symbols inside the bracket { } ex. File_{yyyyMMdd}');
    await expect.soft(page.getByRole('cell', { name: 'Symbol' })).toHaveText('Symbol');
    await expect.soft(page.getByRole('cell', { name: 'Description' })).toHaveText('Description');
    await expect.soft(page.getByRole('cell', { name: 'Examples' })).toHaveText('Examples');
    await expect.soft(page.getByRole('cell', { name: 'companyTaxId' })).toHaveText('companyTaxId');
    await expect.soft(page.getByRole('cell', { name: 'Company Tax ID as a 13-digit' })).toHaveText('Company Tax ID as a 13-digit');
    await expect.soft(page.getByRole('cell', { name: '1234567890123' })).toHaveText('1234567890123');
    await expect.soft(page.getByRole('cell', { name: 'companyAbbr' })).toHaveText('companyAbbr');
    await expect.soft(page.getByRole('cell', { name: 'Company Abbreviation' })).toHaveText('Company Abbreviation');
    await expect.soft(page.getByRole('cell', { name: 'ABC, GKS,...' })).toHaveText('ABC, GKS,...');
    await expect.soft(page.getByRole('cell', { name: 'group', exact: true })).toHaveText('group');
    await expect.soft(page.getByRole('cell', { name: 'The name of group user' })).toHaveText('The name of group user');
    await expect.soft(page.getByRole('cell', { name: 'Default' })).toHaveText('Default');
    await expect.soft(page.getByRole('cell', { name: 'typeCode' })).toHaveText('typeCode');
    await expect.soft(page.getByRole('cell', { name: 'The type code of instrument' })).toHaveText('The type code of instrument');
    await expect.soft(page.getByRole('cell', { name: '1,2,3,4,...' })).toHaveText('1,2,3,4,...');
    await expect.soft(page.getByRole('cell', { name: 'contractNo', exact: true })).toHaveText('contractNo');
    await expect.soft(page.getByRole('cell', { name: 'The Contract No. of instrument' })).toHaveText('The Contract No. of instrument');
    await expect.soft(page.getByRole('cell', { name: 'ContractNo001' })).toHaveText('ContractNo001');
    await expect.soft(page.getByRole('cell', { name: 'receiptNo', exact: true })).toHaveText('receiptNo');
    await expect.soft(page.getByRole('cell', { name: 'The Receipt No. of instrument' })).toHaveText('The Receipt No. of instrument');
    await expect.soft(page.getByRole('cell', { name: 'ReceiptNo001' })).toHaveText('ReceiptNo001');
    await expect.soft(page.getByRole('cell', { name: 'upload:', exact: true })).toHaveText('upload:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use upload date' })).toHaveText('A prefix to use upload date');
    await expect.soft(page.getByRole('cell', { name: 'upload:yyyyMMdd-HHmmssSSS -> 20241231-014530617' })).toHaveText('upload:yyyyMMdd-HHmmssSSS -> 20241231-014530617');
    await expect.soft(page.getByRole('cell', { name: 'submit:', exact: true })).toHaveText('submit:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use submit date' })).toHaveText('A prefix to use submit date');
    await expect.soft(page.getByRole('cell', { name: 'submit:yyyyMMdd-HHmmssSSS -> 20241231-014530617' })).toHaveText('submit:yyyyMMdd-HHmmssSSS -> 20241231-014530617');
    await expect.soft(page.getByRole('cell', { name: 'creation:', exact: true })).toHaveText('creation:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use creation date' })).toHaveText('A prefix to use creation date');
    await expect.soft(page.getByRole('cell', { name: 'creation:yyyyMMdd -> 20241231' })).toHaveText('creation:yyyyMMdd -> 20241231');
    await expect.soft(page.getByRole('cell', { name: 'expired:', exact: true })).toHaveText('expired:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use expired date' })).toHaveText('A prefix to use expired date');
    await expect.soft(page.getByRole('cell', { name: 'expired:yyyyMMdd -> 20241231' })).toHaveText('expired:yyyyMMdd -> 20241231');
    await expect.soft(page.getByRole('cell', { name: 'receipt:', exact: true })).toHaveText('receipt:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use receipt date' })).toHaveText('A prefix to use receipt date');
    await expect.soft(page.getByRole('cell', { name: 'receipt:yyyyMMdd -> 20241231' })).toHaveText('receipt:yyyyMMdd -> 20241231');
    await expect.soft(page.getByRole('cell', { name: 'yyyy', exact: true })).toHaveText('yyyy');
    await expect.soft(page.getByRole('cell', { name: 'Year as a four-digit Number' })).toHaveText('Year as a four-digit Number');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 2024' })).toHaveText('2024-12-31 -> 2024');
    await expect.soft(page.getByRole('cell', { name: 'yy', exact: true })).toHaveText('yy');
    await expect.soft(page.getByRole('cell', { name: 'Year , from 00 to 99' })).toHaveText('Year , from 00 to 99');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 24' })).toHaveText('2024-12-31 -> 24');
    await expect.soft(page.getByRole('cell', { name: 'MM', exact: true })).toHaveText('MM');
    await expect.soft(page.getByRole('cell', { name: 'Month, from 01 through 12' })).toHaveText('Month, from 01 through 12');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 12' })).toHaveText('2024-12-31 -> 12');
    await expect.soft(page.getByRole('cell', { name: 'dd', exact: true })).toHaveText('dd');
    await expect.soft(page.getByRole('cell', { name: 'Day, from 01 through 31' })).toHaveText('Day, from 01 through 31');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 31' })).toHaveText('2024-12-31 -> 31');
    await expect.soft(page.getByRole('cell', { name: 'HH', exact: true })).toHaveText('HH');
    await expect.soft(page.getByRole('cell', { name: 'The hour, using a 24-hour clock from 00 to 23' })).toHaveText('The hour, using a 24-hour clock from 00 to 23');
    await expect.soft(page.getByRole('cell', { name: '01:45:30 -> 01' })).toHaveText('01:45:30 -> 01');
    await expect.soft(page.getByRole('cell', { name: 'mm', exact: true })).toHaveText('mm');
    await expect.soft(page.getByRole('cell', { name: 'The minute, from 00 through 59' })).toHaveText('The minute, from 00 through 59');
    await expect.soft(page.getByRole('cell', { name: '01:45:30 -> 45' })).toHaveText('01:45:30 -> 45');
    await expect.soft(page.getByRole('cell', { name: 'ss', exact: true })).toHaveText('ss');
    await expect.soft(page.getByRole('cell', { name: 'The second, from 00 through 59' })).toHaveText('The second, from 00 through 59');
    await expect.soft(page.getByRole('cell', { name: '01:45:30 -> 30' })).toHaveText('01:45:30 -> 30');
    await expect.soft(page.getByRole('cell', { name: 'SSS', exact: true })).toHaveText('SSS');
    await expect.soft(page.getByRole('cell', { name: 'The milliseconds in a date and time value' })).toHaveText('The milliseconds in a date and time value');
    await expect.soft(page.getByRole('cell', { name: '01:45:30.617 -> 617' })).toHaveText('01:45:30.617 -> 617');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/04. Edit Export Receipts/02. Path Convention.png' });
    await page.waitForTimeout(1000);
    await page.getByRole('dialog').press('Escape');
    await page.waitForTimeout(500)
    await page.locator('label').filter({ hasText: 'File Name info' }).locator('mat-icon').click();
    await page.waitForTimeout(500)




    await expect.soft(page.getByRole('heading', { name: 'Naming Convention' })).toHaveText('Naming Convention');
    await expect.soft(page.getByText('Place symbols inside the bracket { } ex. File_{yyyyMMdd}')).toHaveText('Place symbols inside the bracket { } ex. File_{yyyyMMdd}');
    await expect.soft(page.getByRole('cell', { name: 'Symbol' })).toHaveText('Symbol');
    await expect.soft(page.getByRole('cell', { name: 'Description' })).toHaveText('Description');
    await expect.soft(page.getByRole('cell', { name: 'Examples' })).toHaveText('Examples');
    await expect.soft(page.getByRole('cell', { name: 'companyTaxId' })).toHaveText('companyTaxId');
    await expect.soft(page.getByRole('cell', { name: 'Company Tax ID as a 13-digit' })).toHaveText('Company Tax ID as a 13-digit');
    await expect.soft(page.getByRole('cell', { name: '1234567890123' })).toHaveText('1234567890123');
    await expect.soft(page.getByRole('cell', { name: 'companyAbbr' })).toHaveText('companyAbbr');
    await expect.soft(page.getByRole('cell', { name: 'Company Abbreviation' })).toHaveText('Company Abbreviation');
    await expect.soft(page.getByRole('cell', { name: 'ABC, GKS,...' })).toHaveText('ABC, GKS,...');
    await expect.soft(page.getByRole('cell', { name: 'group', exact: true })).toHaveText('group');
    await expect.soft(page.getByRole('cell', { name: 'The name of group user' })).toHaveText('The name of group user');
    await expect.soft(page.getByRole('cell', { name: 'Default' })).toHaveText('Default');
    await expect.soft(page.getByRole('cell', { name: 'typeCode' })).toHaveText('typeCode');
    await expect.soft(page.getByRole('cell', { name: 'The type code of instrument' })).toHaveText('The type code of instrument');
    await expect.soft(page.getByRole('cell', { name: '1,2,3,4,...' })).toHaveText('1,2,3,4,...');
    await expect.soft(page.getByRole('cell', { name: 'contractNo', exact: true })).toHaveText('contractNo');
    await expect.soft(page.getByRole('cell', { name: 'The Contract No. of instrument' })).toHaveText('The Contract No. of instrument');
    await expect.soft(page.getByRole('cell', { name: 'ContractNo001' })).toHaveText('ContractNo001');
    await expect.soft(page.getByRole('cell', { name: 'receiptNo', exact: true })).toHaveText('receiptNo');
    await expect.soft(page.getByRole('cell', { name: 'The Receipt No. of instrument' })).toHaveText('The Receipt No. of instrument');
    await expect.soft(page.getByRole('cell', { name: 'ReceiptNo001' })).toHaveText('ReceiptNo001');
    await expect.soft(page.getByRole('cell', { name: 'upload:', exact: true })).toHaveText('upload:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use upload date' })).toHaveText('A prefix to use upload date');
    await expect.soft(page.getByRole('cell', { name: 'upload:yyyyMMdd-HHmmssSSS -> 20241231-014530617' })).toHaveText('upload:yyyyMMdd-HHmmssSSS -> 20241231-014530617');
    await expect.soft(page.getByRole('cell', { name: 'submit:', exact: true })).toHaveText('submit:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use submit date' })).toHaveText('A prefix to use submit date');
    await expect.soft(page.getByRole('cell', { name: 'submit:yyyyMMdd-HHmmssSSS -> 20241231-014530617' })).toHaveText('submit:yyyyMMdd-HHmmssSSS -> 20241231-014530617');
    await expect.soft(page.getByRole('cell', { name: 'creation:', exact: true })).toHaveText('creation:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use creation date' })).toHaveText('A prefix to use creation date');
    await expect.soft(page.getByRole('cell', { name: 'creation:yyyyMMdd -> 20241231' })).toHaveText('creation:yyyyMMdd -> 20241231');
    await expect.soft(page.getByRole('cell', { name: 'expired:', exact: true })).toHaveText('expired:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use expired date' })).toHaveText('A prefix to use expired date');
    await expect.soft(page.getByRole('cell', { name: 'expired:yyyyMMdd -> 20241231' })).toHaveText('expired:yyyyMMdd -> 20241231');
    await expect.soft(page.getByRole('cell', { name: 'receipt:', exact: true })).toHaveText('receipt:');
    await expect.soft(page.getByRole('cell', { name: 'A prefix to use receipt date' })).toHaveText('A prefix to use receipt date');
    await expect.soft(page.getByRole('cell', { name: 'receipt:yyyyMMdd -> 20241231' })).toHaveText('receipt:yyyyMMdd -> 20241231');
    await expect.soft(page.getByRole('cell', { name: 'yyyy', exact: true })).toHaveText('yyyy');
    await expect.soft(page.getByRole('cell', { name: 'Year as a four-digit Number' })).toHaveText('Year as a four-digit Number');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 2024' })).toHaveText('2024-12-31 -> 2024');
    await expect.soft(page.getByRole('cell', { name: 'yy', exact: true })).toHaveText('yy');
    await expect.soft(page.getByRole('cell', { name: 'Year , from 00 to 99' })).toHaveText('Year , from 00 to 99');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 24' })).toHaveText('2024-12-31 -> 24');
    await expect.soft(page.getByRole('cell', { name: 'MM', exact: true })).toHaveText('MM');
    await expect.soft(page.getByRole('cell', { name: 'Month, from 01 through 12' })).toHaveText('Month, from 01 through 12');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 12' })).toHaveText('2024-12-31 -> 12');
    await expect.soft(page.getByRole('cell', { name: 'dd', exact: true })).toHaveText('dd');
    await expect.soft(page.getByRole('cell', { name: 'Day, from 01 through 31' })).toHaveText('Day, from 01 through 31');
    await expect.soft(page.getByRole('cell', { name: '2024-12-31 -> 31' })).toHaveText('2024-12-31 -> 31');
    await expect.soft(page.getByRole('cell', { name: 'HH', exact: true })).toHaveText('HH');
    await expect.soft(page.getByRole('cell', { name: 'The hour, using a 24-hour clock from 00 to 23' })).toHaveText('The hour, using a 24-hour clock from 00 to 23');
    await expect.soft(page.getByRole('cell', { name: '01:45:30 -> 01' })).toHaveText('01:45:30 -> 01');
    await expect.soft(page.getByRole('cell', { name: 'mm', exact: true })).toHaveText('mm');
    await expect.soft(page.getByRole('cell', { name: 'The minute, from 00 through 59' })).toHaveText('The minute, from 00 through 59');
    await expect.soft(page.getByRole('cell', { name: '01:45:30 -> 45' })).toHaveText('01:45:30 -> 45');
    await expect.soft(page.getByRole('cell', { name: 'ss', exact: true })).toHaveText('ss');
    await expect.soft(page.getByRole('cell', { name: 'The second, from 00 through 59' })).toHaveText('The second, from 00 through 59');
    await expect.soft(page.getByRole('cell', { name: '01:45:30 -> 30' })).toHaveText('01:45:30 -> 30');
    await expect.soft(page.getByRole('cell', { name: 'SSS', exact: true })).toHaveText('SSS');
    await expect.soft(page.getByRole('cell', { name: 'The milliseconds in a date and time value' })).toHaveText('The milliseconds in a date and time value');
    await expect.soft(page.getByRole('cell', { name: '01:45:30.617 -> 617' })).toHaveText('01:45:30.617 -> 617');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/04. Edit Export Receipts/03. File Name Convention.png' });
    await page.waitForTimeout(1000);
    await page.getByRole('dialog').press('Escape');
    await page.waitForTimeout(1000);
    await page.getByLabel('Select Server SFTPzDOX').selectOption('SFTP');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/04. Edit Export Receipts/04. Response SFTP.png' });
    await page.waitForTimeout(1000);
    await page.getByLabel('Select Server SFTPzDOX').selectOption('zDOX');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/04. Edit Export Receipts/05. Response zDOX Details.png' });
    await page.waitForTimeout(1000);
    await page.getByRole('button', { name: 'Cancel' }).click();



});













test('TC08 Delete Organization ', async ({ page }) => {
    await page.getByRole('link', { name: 'Organization' }).click();
    await page.getByRole('row', { name: 'Automate Test ทดสอบอัตโนมัติ AT' }).getByRole('button').nth(1).click();
    await expect.soft(page.getByLabel('Confirm delete organization')).toBeVisible();
    await page.getByRole('button', { name: 'Cancel' }).click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/01. Creation/04. Click Cancel Delete Or.png' });
    await page.waitForTimeout(1500);
    await page.getByRole('row', { name: 'Automate Test ทดสอบอัตโนมัติ AT' }).getByRole('button').nth(1).click();
    await expect.soft(page.getByLabel('Confirm delete organization')).toBeVisible();
    await page.getByRole('button', { name: 'Confirm' }).click();
    await page.waitForTimeout(1500)
    await page.screenshot({ path: 'Output/TS06-Settings/TC08 Creation Organization/01. Creation/05. Click Confirm Delete Or.png' });
    await page.waitForTimeout(1500)



});





test('TC09 Creation Company General Information  ', async ({ page }) => {
    await page.getByRole('link', { name: 'Organization' }).click();
    await page.getByRole('tab', { name: 'Company' }).click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC09 Creation Company/01. All Company.png' });
    await page.locator('div').filter({ hasText: /^OrganizationAll$/ }).first().click();
    await page.waitForTimeout(1500);
    await page.getByRole('option', { name: 'Test Auto' }).locator('span').click();
    await page.getByRole('button', { name: 'Add' }).click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC09 Creation Company/02. Company Details.png' });
    await page.locator('input[name="nameEng"]').click();
    await page.locator('input[name="nameTha"]').click();
    await page.locator('input[name="taxId"]').click();
    await page.locator('input[name="abbrName"]').click();
    await page.locator('input[name="keyStoreKey"]').click();
    await page.locator('input[name="keyStorePass"]').click();
    await page.locator('input[name="userId"]').click();
    await page.locator('input[name="password"]').click();
    await page.locator('input[name="nameEng"]').click();
    await page.waitForTimeout(1500);
    await expect.soft(page.locator('div').filter({ hasText: /^Name \(English\)\*Name is required$/ }).locator('div')).toHaveText('Name is required');
    await expect.soft(page.locator('div').filter({ hasText: /^Name \(Thai\)\*Name is required$/ }).locator('div')).toHaveText('Name is required');
    await expect.soft(page.getByText('Tax ID is required')).toHaveText('Tax ID is required');
    await expect.soft(page.getByText('Company Abbreviation is required')).toHaveText('Company Abbreviation is required');
    // await expect.soft(page.getByText('keyStoreKey is required')).toHaveText('keyStoreKey is required');
    // // await expect.soft(page.getByText('keyStorePass is required')).toHaveText('keyStorePass is required');
    // await expect.soft(page.getByText('UserId is required')).toHaveText('UserId is required');
    // await expect.soft(page.getByText('Password is required')).toHaveText('Password is required');
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC09 Creation Company/03. Company Required.png' });
    await page.waitForTimeout(1500);
    // await page.getByText('Password is required').hover();
    // await page.waitForTimeout(500);
    // await page.screenshot({ path: 'Output/TS06-Settings/TC09 Creation Company/04. Company Required 2.png' });

});



test('TC09 Creation Company  ', async ({ page }) => {
    await page.getByRole('link', { name: 'Organization' }).click();
    await page.getByRole('tab', { name: 'Company' }).click();
    await page.waitForTimeout(1500);
    await page.locator('div').filter({ hasText: /^OrganizationAll$/ }).first().click();
    await page.getByRole('option', { name: 'Test Auto' }).locator('span').click();
    await page.getByRole('button', { name: 'Add' }).click();
    await page.waitForTimeout(1500);
    await page.locator('input[name="nameEng"]').fill('Playwright');
    await page.locator('input[name="nameTha"]').fill('นักเขียนบทละคร');
    await page.locator('input[name="taxId"]').fill('2536433718231');
    await page.locator('input[name="abbrName"]').fill('PW');
    await page.locator('input[name="keyStoreKey"]').fill('test');
    await page.locator('input[name="keyStorePass"]').fill('test');
    await page.locator('input[name="userId"]').fill('test');
    await page.locator('input[name="password"]').fill('test');
    await page.locator('#file').setInputFiles('Data Files/AutomateTest.p12');
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC09 Creation Company/05. Input Company.png' });
    await page.waitForTimeout(1000);
    await page.getByRole('button', { name: 'Cancel' }).click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC09 Creation Company/06. Click Cancle Company.png' });
    await page.waitForTimeout(1500);
    await page.getByRole('button', { name: 'Add' }).click();
    await page.waitForTimeout(1500);
    await page.locator('input[name="nameEng"]').fill('Playwright');
    await page.locator('input[name="nameTha"]').fill('นักเขียนบทละคร');
    await page.locator('input[name="taxId"]').fill('2536433718231');
    await page.locator('input[name="abbrName"]').fill('PW');
    await page.locator('input[name="keyStoreKey"]').fill('test');
    await page.locator('input[name="keyStorePass"]').fill('test');
    await page.locator('input[name="userId"]').fill('test');
    await page.locator('input[name="password"]').fill('test');
    await page.locator('#file').setInputFiles('Data Files/AutomateTest.p12');
    await page.waitForTimeout(1500);
    await page.getByRole('button', { name: 'Add' }).click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'Output/TS06-Settings/TC09 Creation Company/07. Click Add Company.png' });


});



test('TC10 Delete Company  ', async ({ page }) => {
    await page.getByRole('link', { name: 'Organization' }).click();
    await page.getByRole('tab', { name: 'Company' }).click();
    await page.waitForTimeout(1500);
    await page.locator('div').filter({ hasText: /^OrganizationAll$/ }).first().click();
    await page.getByRole('option', { name: 'Test Auto' }).locator('span').click();
    await page.waitForTimeout(1500);
    await page.getByRole('row', { name: 'Playwright นักเขียนบทละคร PW' }).getByRole('button').nth(2).click();
    await page.waitForTimeout(1500);
    await page.getByRole('button', { name: 'Cancel' }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC10 Delete Company/01. Click Cancel Delete.png' });
    await page.waitForTimeout(1500);
    await page.getByRole('row', { name: 'Playwright นักเขียนบทละคร PW' }).getByRole('button').nth(2).click();
    await page.waitForTimeout(1500);
    await page.getByRole('button', { name: 'Confirm' }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC10 Delete Company/02. Click Confirm Delete.png' });
});









test('TC11 Holiday  ', async ({ page }) => {
    await page.getByRole('link', { name: 'Holiday' }).click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'Output/TS06-Settings/TC11 Holiday/01.Default Page.png' });

});
