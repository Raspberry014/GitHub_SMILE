import logging
from playwright.sync_api import Page, expect
from utils.logger import get_logger
from utils.ui_fixes import remove_demoqa_banners

class BasePage:
    def __init__(self, page):
        self.page = page
        self.log = logging.getLogger("demoqa")  # <-- ВОТ ЭТОГО НЕ ХВАТАЛО

    def open(self, path: str):
        self.log.info(f"OPEN {path}")
        self.page.goto(path, wait_until="domcontentloaded", timeout=60000)
        return self

    def click(self, selector: str):
        self.log.info(f"CLICK {selector}")
        self.page.locator(selector).click()

    def fill(self, selector: str, value: str):
        self.log.info(f"FILL {selector} = {value!r}")
        self.page.locator(selector).fill(value)

    def expect_visible(self, selector: str):
        self.log.info(f"EXPECT visible {selector}")
        expect(self.page.locator(selector)).to_be_visible()
        return self

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")