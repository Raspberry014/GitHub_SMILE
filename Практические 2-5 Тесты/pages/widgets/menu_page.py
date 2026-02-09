from playwright.sync_api import expect
from pages.base_page import BasePage


class MenuPage(BasePage):
    PATH = "/menu"

    def open_page(self):
        return self.open(self.PATH)

    def hover_main_item_2(self):
        item = self.page.locator("a:has-text('Main Item 2')")
        item.hover()

    def hover_sub_sub_list(self):
        sub = self.page.locator("a:has-text('SUB SUB LIST')")
        sub.hover()

    def assert_sub_items_visible(self):
        expect(self.page.locator("a:has-text('Sub Item')").first).to_be_visible()
        expect(self.page.locator("a:has-text('SUB SUB LIST')")).to_be_visible()

    def assert_sub_sub_items_visible(self):
        expect(self.page.locator("a:has-text('Sub Sub Item 1')")).to_be_visible()
        expect(self.page.locator("a:has-text('Sub Sub Item 2')")).to_be_visible()

    def click_sub_sub_item_2(self):
        self.page.locator("a:has-text('Sub Sub Item 2')").click()
