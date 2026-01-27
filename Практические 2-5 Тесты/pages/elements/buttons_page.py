from playwright.sync_api import expect
from pages.base_page import BasePage

class ButtonsPage(BasePage):
    PATH = "/buttons"

    def open_page(self):
        return self.open(self.PATH)

    def double_click(self):
        self.page.locator("#doubleClickBtn").dblclick()
        return self

    def right_click(self):
        self.page.locator("#rightClickBtn").click(button="right")
        return self

    def dynamic_click(self):
        btn = self.page.locator("#dynamicClickBtn")
        if btn.count() == 0:
            btn = self.page.get_by_role("button", name="Click Me", exact=True).last
        btn.scroll_into_view_if_needed()
        btn.click()
        return self

    def assert_messages(self):
        expect(self.page.locator("#doubleClickMessage")).to_be_visible()
        expect(self.page.locator("#rightClickMessage")).to_be_visible()
        expect(self.page.locator("#dynamicClickMessage")).to_be_visible()
