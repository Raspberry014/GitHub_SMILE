from playwright.sync_api import expect
from pages.base_page import BasePage

class AlertsPage(BasePage):
    PATH = "/alerts"

    def open_page(self):
        return self.open(self.PATH)

    def handle_simple_alert(self):
        self.page.once("dialog", lambda d: d.accept())
        self.page.locator("#alertButton").click()

    def handle_timer_alert(self):
        self.page.once("dialog", lambda d: d.accept())
        self.page.locator("#timerAlertButton").click()

    def handle_confirm_ok(self):
        self.page.once("dialog", lambda d: d.accept())
        self.page.locator("#confirmButton").click()
        expect(self.page.locator("#confirmResult")).to_contain_text("Ok")

    def handle_confirm_cancel(self):
        self.page.once("dialog", lambda d: d.dismiss())
        self.page.locator("#confirmButton").click()
        expect(self.page.locator("#confirmResult")).to_contain_text("Cancel")

    def handle_prompt(self, text: str):
        self.page.once("dialog", lambda d: d.accept(text))
        self.page.locator("#promtButton").click()
        expect(self.page.locator("#promptResult")).to_contain_text(text)
