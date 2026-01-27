from playwright.sync_api import expect
from pages.base_page import BasePage

class ModalDialogsPage(BasePage):
    PATH = "/modal-dialogs"

    def open_page(self):
        return self.open(self.PATH)

    def open_small_and_close_button(self):
        self.page.click("#showSmallModal")
        expect(self.page.locator(".modal-content")).to_be_visible()
        self.page.click("#closeSmallModal")
        expect(self.page.locator(".modal-content")).not_to_be_visible()

    def open_large_and_close_x(self):
        self.page.click("#showLargeModal")
        expect(self.page.locator(".modal-content")).to_be_visible()
        # close by 'x' icon
        self.page.locator(".modal-header button.close").click()
        expect(self.page.locator(".modal-content")).not_to_be_visible()
