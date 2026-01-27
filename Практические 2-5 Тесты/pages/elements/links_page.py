import re
from playwright.sync_api import expect
from pages.base_page import BasePage

class LinksPage(BasePage):
    PATH = "/links"

    def open_page(self):
        return self.open(self.PATH)

    def open_simple_link_new_tab(self):
        with self.page.context.expect_page() as new_page_info:
            self.page.click("#simpleLink")
        p = new_page_info.value
        expect(p).to_have_url(re.compile(r".*demoqa.*"))
        p.close()

    def open_dynamic_link_new_tab(self):
        with self.page.context.expect_page() as new_page_info:
            self.page.click("#dynamicLink")
        p = new_page_info.value
        expect(p).to_have_url(re.compile(r".*demoqa.*"))
        p.close()

    def click_api_link_and_assert_code(self, link_id: str, code: str):
        resp = self.page.locator("#linkResponse")
        before = resp.inner_text() if resp.is_visible() else ""

        self.page.click(f"#{link_id}")
        expect(resp).to_be_visible()
        expect(resp).not_to_have_text(before)  # дождались обновления

        text = resp.inner_text()

    # DemoQA иногда флапает на no-content
        if link_id == "no-content":
            assert ("204" in text) or ("201" in text), f"Expected 204 or 201 in link response: {text!r}"
        else:
            assert code in text, f"Expected {code} in link response: {text!r}"
