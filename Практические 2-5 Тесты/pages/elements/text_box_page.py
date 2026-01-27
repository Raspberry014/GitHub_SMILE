from playwright.sync_api import expect
from pages.base_page import BasePage

class TextBoxPage(BasePage):
    PATH = "/text-box"

    def open_page(self):
        return self.open(self.PATH)

    def fill_form(self, full_name: str, email: str, current_addr: str, permanent_addr: str):
        self.fill("#userName", full_name)
        self.fill("#userEmail", email)
        self.fill("#currentAddress", current_addr)
        self.fill("#permanentAddress", permanent_addr)
        self.click("#submit")

    def assert_output(self, full_name: str, email: str, current_addr: str, permanent_addr: str):
        out = self.page.locator("#output")
        expect(out).to_be_visible()
        expect(out.locator("#name")).to_contain_text(full_name)
        expect(out.locator("#email")).to_contain_text(email)
        expect(out.locator("p#currentAddress")).to_contain_text(current_addr)
        expect(out.locator("p#permanentAddress")).to_contain_text(permanent_addr)

    def assert_invalid_email(self):
        # DemoQA marks invalid email by class on the input (commonly "field-error").
        cls = self.page.locator("#userEmail").get_attribute("class") or ""
        assert "field-error" in cls, f"Expected 'field-error' in class, got: {cls!r}"
