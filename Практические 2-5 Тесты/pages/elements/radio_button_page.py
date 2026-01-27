from playwright.sync_api import expect
from pages.base_page import BasePage

class RadioButtonPage(BasePage):
    PATH = "/radio-button"

    def open_page(self):
        return self.open(self.PATH)

    def choose_yes(self):
        self.page.get_by_text("Yes", exact=True).click()
        return self

    def choose_impressive(self):
        self.page.get_by_text("Impressive", exact=True).click()
        return self

    def assert_no_disabled(self):
        # "No" radio is disabled in DemoQA
        disabled = self.page.locator("#noRadio").is_disabled()
        assert disabled is True

    def assert_result(self, expected: str):
        expect(self.page.locator(".text-success")).to_have_text(expected)
