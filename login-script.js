/**
 * @param {puppeteer.Browser} browser
 * @param {{url: string, options: LHCI.CollectCommand.Options}} context
 */
module.exports = async (browser, context) => {
  // launch browser for LHCI
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:5000');
  await page.type('#username', 'test');
  await page.click('[data-icon="arrow_forward"]');
  await page.waitForNavigation();
  // close session for next run
  await page.close();
};
