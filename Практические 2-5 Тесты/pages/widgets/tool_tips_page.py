from playwright.sync_api import expect
from pages.base_page import BasePage


class ToolTipsPage(BasePage):
    PATH = "/tool-tips"

    def open_page(self):
        return self.open(self.PATH)

    def _tooltip(self):
        return self.page.locator(".tooltip-inner")

    def hover_button(self):
        self.page.hover("#toolTipButton")

    def hover_input(self):
        self.page.hover("#toolTipTextField")

    def hover_contrary_text(self):
        # "Contrary" word is inside a paragraph
        self.page.hover("text=Contrary")

    def hover_link(self, link_text: str = "1.10.32"):
        self.page.hover(f"a:has-text('{link_text}')")

    def assert_tooltip_text(self, expected: str):
        tip = self._tooltip()
        expect(tip).to_be_visible()
        expect(tip).to_have_text(expected)
