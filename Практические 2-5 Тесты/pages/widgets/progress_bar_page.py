from playwright.sync_api import expect
from pages.base_page import BasePage

class ProgressBarPage(BasePage):
    PATH = "/progress-bar"

    START_BTN = "#startStopButton"
    RESET_BTN = "#resetButton"
    BAR = "#progressBar"

    def open_page(self):
        return self.open(self.PATH)

    def start(self):
        self.page.click(self.START_BTN)

    def wait_until(self, percent: str):
        expect(self.page.locator(self.BAR)).to_have_attribute(
            "aria-valuenow", percent
        )

    def reset(self):
        self.page.click(self.RESET_BTN)
