from playwright.sync_api import expect
from pages.base_page import BasePage


class SelectMenuPage(BasePage):
    PATH = "/select-menu"

    def open_page(self):
        return self.open(self.PATH)

    # ---- react-select helpers ----
    def _choose_react_select(self, input_selector: str, option_text: str):
        inp = self.page.locator(input_selector)
        inp.click()
        inp.fill(option_text)
        inp.press("Enter")

    def choose_select_value(self, option_text: str):
        # Select Value (with OptGroup)
        self._choose_react_select("#react-select-2-input", option_text)

    def choose_select_one(self, option_text: str):
        # Select One
        self._choose_react_select("#react-select-3-input", option_text)

    def choose_multi_select(self, options: list[str]):
        # Multiselect drop down
        inp = self.page.locator("#react-select-4-input")
        for opt in options:
            inp.click()
            inp.fill(opt)
            inp.press("Enter")

    def choose_old_style_color(self, color: str):
        # Old Style Select Menu
        self.page.select_option("#oldSelectMenu", label=color)

    def choose_standard_multi(self, labels: list[str]):
        # Standard multi select
        self.page.select_option("#cars", label=labels)

    # ---- assertions ----
    def assert_select_value_contains(self, text: str):
        expect(self.page.locator("#withOptGroup")).to_contain_text(text)

    def assert_select_one_contains(self, text: str):
        expect(self.page.locator("#selectOne")).to_contain_text(text)

    def assert_multi_select_contains(self, text: str):
        # selected values appear as chips within the container
        expect(self.page.locator("#selectMenuContainer")).to_contain_text(text)

    def assert_old_style_selected(self, color: str):
        expect(self.page.locator("#oldSelectMenu option:checked")).to_have_text(color)

    def assert_standard_multi_selected(self, labels: list[str]):
        selected = self.page.locator("#cars option:checked").all_inner_texts()
        for lbl in labels:
            assert lbl in selected
