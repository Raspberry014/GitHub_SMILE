from pathlib import Path
from playwright.sync_api import expect
from pages.base_page import BasePage

class PracticeFormPage(BasePage):
    PATH = "/automation-practice-form"

    def open_page(self):
        return self.open(self.PATH)

    def fill_main(self, first, last, email, mobile):
        self.fill("#firstName", first)
        self.fill("#lastName", last)
        self.fill("#userEmail", email)
        self.fill("#userNumber", mobile)

    def select_gender(self, gender: str):
        # gender: "Male" | "Female" | "Other"
        self.page.get_by_text(gender, exact=True).click()

    def set_birth_date(self, value: str):
        # e.g. "10 Oct 2000"
        self.page.locator("#dateOfBirthInput").click()
        self.page.locator("#dateOfBirthInput").fill(value)
        self.page.keyboard.press("Enter")

    def add_subject(self, subject: str):
        inp = self.page.locator("#subjectsInput")
        inp.scroll_into_view_if_needed()
        inp.click(force=True)
        inp.fill(subject)

        option = self.page.locator("div[id^='react-select-2-option-']").filter(has_text=subject).first
        option.wait_for(state="visible")
        option.click()

        expect(self.page.locator(".subjects-auto-complete__multi-value__label")).to_contain_text(subject)

    def select_hobby(self, hobby: str):
    # если внезапно появился overlay/modal — закрываем
        overlay_close = self.page.locator("button.btn-close, button.close, .modal-header button")
        if overlay_close.count() > 0:
            try:
                overlay_close.first.click(timeout=1000)
            except Exception:
                pass

        label = self.page.locator("label.custom-control-label").filter(has_text=hobby).first
        label.scroll_into_view_if_needed()
        try:
            label.click()
        except Exception:
            label.click(force=True)
        return self

    def upload_picture(self, filepath: str):
        p = Path(filepath)
        assert p.exists(), f"File not found: {filepath}"
        self.page.set_input_files("#uploadPicture", str(p))

    def fill_address(self, address: str):
        self.fill("#currentAddress", address)

    def _close_modal_if_any(self):
        modal = self.page.locator("div.modal.show")
        if modal.count() > 0:
            try:
                self.page.keyboard.press("Escape")
            except Exception:
                pass

        close_btn = modal.locator("button.btn-close, button.close, .modal-header button")
        if close_btn.count() > 0:
            try:
                close_btn.first.click(timeout=1000)
            except Exception:
                pass

        # крайний случай — прячем модалку, чтобы не перехватывала клики
        try:
            self.page.evaluate("""
                () => document.querySelectorAll('div.modal.show').forEach(m => {
                    m.style.display='none';
                    m.style.pointerEvents='none';
                })
            """)
        except Exception:
            pass

    def select_state_city(self, state: str, city: str):
        self._close_modal_if_any()

        state_box = self.page.locator("#state")
        state_box.scroll_into_view_if_needed()
        try:
            state_box.click()
        except Exception:
            state_box.click(force=True)

        self.page.get_by_text(state, exact=True).click()

        self._close_modal_if_any()

        city_box = self.page.locator("#city")
        city_box.scroll_into_view_if_needed()
        try:
            city_box.click()
        except Exception:
            city_box.click(force=True)

        self.page.get_by_text(city, exact=True).click()
        return self

    def submit(self):
        # On DemoQA submit can be below viewport
        self.page.locator("#submit").scroll_into_view_if_needed()
        self.page.locator("#submit").click()

    def assert_modal_contains(self, pairs: dict):
        title = self.page.locator("#example-modal-sizes-title-lg")
        expect(title).to_be_visible()
        table = self.page.locator(".table-responsive")
        expect(table).to_be_visible()
        text = table.inner_text()
        for k, v in pairs.items():
            assert k in text and v in text, f"Missing {k}:{v} in modal table"

    def assert_not_submitted(self):
        # If form wasn't submitted, modal should not be visible
        expect(self.page.locator("#example-modal-sizes-title-lg")).not_to_be_visible()

    def assert_required_invalid(self):
        # Using browser validity checks
        assert self.page.locator("#firstName").evaluate("el => el.checkValidity()") is False
        assert self.page.locator("#lastName").evaluate("el => el.checkValidity()") is False
        assert self.page.locator("#userNumber").evaluate("el => el.checkValidity()") is False
