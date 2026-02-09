import re
from playwright.sync_api import expect
from pages.base_page import BasePage


class SelectablePage(BasePage):
    PATH = "/selectable"

    def open_page(self):
        return self.open(self.PATH)

    def list_item(self, text: str):
        return self.page.locator("#verticalListContainer li", has_text=text)

    def click_item(self, text: str, *, ctrl: bool = False):
        item = self.list_item(text)
        expect(item).to_be_visible()
        if ctrl:
            self.page.keyboard.down("Control")
            item.click()
            self.page.keyboard.up("Control")
        else:
            item.click()

    def assert_selected(self, text: str):
        expect(self.list_item(text)).to_have_class(re.compile(r".*active.*"))

    def assert_not_selected(self, text: str):
        expect(self.list_item(text)).not_to_have_class(re.compile(r".*active.*"))
