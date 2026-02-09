from playwright.sync_api import expect
from pages.base_page import BasePage


class TabsPage(BasePage):
    PATH = "/tabs"

    def open_page(self):
        return self.open(self.PATH)

    def click_tab(self, name: str):
        key = name.strip().lower()
        mapping = {
            "what": "#demo-tab-what",
            "origin": "#demo-tab-origin",
            "use": "#demo-tab-use",
            "more": "#demo-tab-more",
        }
        sel = mapping.get(key, name)  # allow passing selector directly
        self.page.locator(sel).click()

    def assert_tab_content_visible(self, tab: str, must_contain: str | None = None):
        key = tab.strip().lower()
        panel_map = {
            "what": "#demo-tabpane-what",
            "origin": "#demo-tabpane-origin",
            "use": "#demo-tabpane-use",
            "more": "#demo-tabpane-more",
        }
        panel = self.page.locator(panel_map[key])
        expect(panel).to_be_visible()
        if must_contain:
            expect(panel).to_contain_text(must_contain)

    def assert_more_disabled(self):
        more = self.page.locator("#demo-tab-more")
        expect(more).to_have_attribute("aria-disabled", "true")
