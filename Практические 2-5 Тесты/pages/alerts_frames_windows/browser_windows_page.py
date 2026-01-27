from playwright.sync_api import expect
from pages.base_page import BasePage

class BrowserWindowsPage(BasePage):
    PATH = "/browser-windows"

    def open_page(self):
        return self.open(self.PATH)

    def open_new_tab_and_check(self):
        with self.page.context.expect_page() as pinfo:
            self.page.click("#tabButton")
        p = pinfo.value
        expect(p.locator("body")).to_contain_text("This is a sample page")
        p.close()

    def open_new_window_and_check(self):
        with self.page.context.expect_page() as pinfo:
            self.page.click("#windowButton")
        p = pinfo.value
        expect(p.locator("body")).to_contain_text("This is a sample page")
        p.close()
