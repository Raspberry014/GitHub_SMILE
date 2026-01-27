from playwright.sync_api import expect
from pages.base_page import BasePage

class CheckBoxPage(BasePage):
    PATH = "/checkbox"

    def open_page(self):
        return self.open(self.PATH)

    def expand_all(self):
        self.click("button[title='Expand all']")
        return self

    def collapse_all(self):
        self.click("button[title='Collapse all']")
        return self

    def select_parent_home(self):
        # Click the checkbox UI near "Home"
        self.page.locator("label[for='tree-node-home'] span.rct-checkbox").click()
        return self

    def select_child_notes(self):
        # Ensure expanded then click "Notes"
        self.page.get_by_text("Home", exact=True).scroll_into_view_if_needed()
        self.page.locator("label[for='tree-node-notes'] span.rct-checkbox").click()
        return self

    def assert_result_contains(self, *tokens: str):
        expect(self.page.locator("#result")).to_be_visible()
        text = " ".join(self.page.locator("#result span.text-success").all_text_contents()).lower()
        for t in tokens:
            assert t.lower() in text, f"Expected token {t!r} in result: {text!r}"
