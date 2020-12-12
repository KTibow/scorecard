import pytest
from pyppeteer import launch, errors as pyppeteer_errors
from os import remove, removedirs, mkdir
from os.path import exists
from glob import glob
import asyncio

# Test every endpoint

try:
    mkdir("pytest_screenshots")
except FileExistsError:
    screenshots = glob(r"pytest_screenshots\*")
    for screenshot in screenshots:
        remove(screenshot)
    removedirs("pytest_screenshots")
    mkdir("pytest_screenshots")


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def browser():
    browser_config = {"autoClose": False, "slowMo": 1}
    if exists(r"C:\Users\Kende\AppData\Local\Google\Chrome\Application\chrome.exe"):
        browser_config[
            "executablePath"
        ] = r"C:\Users\Kende\AppData\Local\Google\Chrome\Application\chrome.exe"
        browser_config["headless"] = False
    browser = await launch(browser_config)
    yield browser
    try:
        await browser.close()
    except Exception:
        pass


@pytest.fixture(scope="function")
async def page(browser):
    page = await browser.newPage()
    page.setDefaultNavigationTimeout(5000)
    databases = glob("*.db")
    for database in databases:
        try:
            remove(database)
        except Exception:
            pass
    yield page
    await page.evaluate("localStorage.clear()")
    await page.close()


@pytest.fixture(scope="function")
async def tabs_2(browser):
    databases = glob("*.db")
    for database in databases:
        try:
            remove(database)
        except Exception:
            pass
    page1 = await browser.newPage()
    page1.setDefaultNavigationTimeout(5000)
    page2 = await browser.newPage()
    page2.setDefaultNavigationTimeout(5000)
    yield [page1, page2]
    try:
        await page1.evaluate("localStorage.clear()")
    except pyppeteer_errors.ElementHandleError:
        pass
    await page1.close()
    try:
        await page2.evaluate("localStorage.clear()")
    except pyppeteer_errors.ElementHandleError:
        pass
    await page2.close()


class TestGeneral(object):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("method", ["keyboard", "button", "localStorage"])
    async def test_login(self, page, method):
        await page.goto("http://127.0.0.1:5000")
        assert "ClueCard | E-ScoreCard for game clues" == await page.title()
        if method == "localStorage":
            await page.evaluate("localStorage.setItem('username', 'Kendell')")
            await page.reload()
            await page.screenshot({"path": "pytest_screenshots/logging_you_in.png"})
        else:
            await page.keyboard.type("Kendell")
            if method == "keyboard":
                await page.keyboard.type("\n")
            else:
                await page.click("button")
        await page.waitForNavigation({"waitUntil": "networkidle2"})
        await page.screenshot({"path": f"pytest_screenshots/login_{method}.png"})
        assert "http://127.0.0.1:5000/cluecard/Kendell" == page.url
        assert "Play ClueCard | E-ScoreCard for game clues" == await page.title()

    @pytest.mark.asyncio
    async def test_update_dbs(self, tabs_2):
        # Do initial add
        for page_index, this_page in enumerate(tabs_2):
            await this_page.goto("http://127.0.0.1:5000")
            await this_page.bringToFront()
            await this_page.keyboard.type(f"Kendell{page_index}")
            await this_page.evaluate("document.querySelector('button').click()")
            await this_page.waitForNavigation({"waitUntil": "networkidle2"})
            await this_page.evaluate("localStorage.clear()")
        main_tab = tabs_2[1]
        await main_tab.bringToFront()
        await main_tab.focus("#userId")
        await main_tab.keyboard.type(await tabs_2[0].evaluate("userIdString"))
        await main_tab.click("#addToGroup")
        # New id
        await this_page.goto("http://127.0.0.1:5000")
        await this_page.keyboard.type("Kendell1")
        await this_page.evaluate("document.querySelector('button').click()")
        await this_page.waitForNavigation({"waitUntil": "networkidle2"})
        await this_page.evaluate("localStorage.clear()")
        await asyncio.sleep(0.5)
        await main_tab.screenshot({"path": "pytest_screenshots/after_update_dbs.png"})
        people_in_group = await main_tab.querySelectorEval(
            "#groupStat", "(el) => {return el.innerHTML}"
        )
        assert people_in_group in [
            "Right now you have Kendell0 and Kendell1 in your group.",
        ]


class TestAddToGroup(object):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_on_old", [True, False])
    @pytest.mark.parametrize("use_keyboard", [True, False])
    async def test_add_to_group_makenew(self, tabs_2, use_on_old, use_keyboard):
        for page_index, this_page in enumerate(tabs_2):
            await this_page.goto("http://127.0.0.1:5000")
            await this_page.bringToFront()
            assert "ClueCard | E-ScoreCard for game clues" == await this_page.title()
            await this_page.keyboard.type(f"Kendell{page_index}")
            await this_page.evaluate("document.querySelector('button').click()")
            await this_page.waitForNavigation({"waitUntil": "networkidle2"})
            await this_page.evaluate("localStorage.clear()")
        main_tab = tabs_2[not use_on_old]
        await main_tab.bringToFront()
        await main_tab.focus("#userId")
        await main_tab.keyboard.type(await tabs_2[use_on_old].evaluate("userIdString"))
        if use_keyboard:
            await main_tab.keyboard.type("\n")
        else:
            await main_tab.click("#addToGroup")
        # After adding
        image_path = "pytest_screenshots/add_to_group"
        image_path += f"_{'same_page' if use_on_old else 'old_page'}"
        image_path += f"_{'with_keyboard' if use_keyboard else 'with_button'}"
        await main_tab.bringToFront()
        await asyncio.sleep(0.5)
        await main_tab.screenshot({"path": image_path + ".png"})
        people_in_group = await main_tab.querySelectorEval(
            "#groupStat", "(el) => {return el.innerHTML}"
        )
        assert people_in_group in [
            "Right now you have Kendell0 and Kendell1 in your group.",
        ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tab_to_add", [[0, 2], [1, 2], [2, 0], [2, 1]])
    async def test_add_to_existing_group(self, page, tabs_2, tab_to_add):
        all_tabs = tabs_2 + [page]
        for page_index, this_page in enumerate(all_tabs):
            await this_page.goto("http://127.0.0.1:5000")
            await this_page.bringToFront()
            assert "ClueCard | E-ScoreCard for game clues" == await this_page.title()
            await this_page.keyboard.type(f"Kendell{page_index}")
            await this_page.evaluate("document.querySelector('button').click()")
            await this_page.waitForNavigation({"waitUntil": "networkidle2"})
            await this_page.evaluate("localStorage.clear()")
            await this_page.evaluate("document.hasFocus = () => {return true;}")
        # First add
        main_tab = all_tabs[0]
        await main_tab.bringToFront()
        user_id = await main_tab.querySelector("#userId")
        await main_tab.type("#userId", await all_tabs[1].evaluate("userIdString"))
        await main_tab.click("#addToGroup")
        await user_id.click(clickCount=3)
        # Second add
        main_tab = all_tabs[tab_to_add[0]]
        await main_tab.bringToFront()
        await main_tab.type(
            "#userId", await all_tabs[tab_to_add[1]].evaluate("userIdString")
        )
        await main_tab.click("#addToGroup")
        # After adding
        image_path = "pytest_screenshots/add_to_existing_group"
        image_path += f"_{tab_to_add}"
        await main_tab.bringToFront()
        await asyncio.sleep(0.5)
        await main_tab.screenshot({"path": image_path + ".png"})
        people_in_group = await main_tab.querySelectorEval(
            "#groupStat", "(el) => {return el.innerHTML}"
        )
        assert people_in_group in [
            "Right now you have Kendell0, Kendell1 and Kendell2 in your group.",
        ]
