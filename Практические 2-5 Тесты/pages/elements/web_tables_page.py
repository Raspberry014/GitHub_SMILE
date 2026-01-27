from playwright.sync_api import expect
from pages.base_page import BasePage

class WebTablesPage(BasePage):
    PATH = "/webtables"

    def open_page(self):
        return self.open(self.PATH)

    def add_record(self, first, last, email, age, salary, department):
        self.click("#addNewRecordButton")
        self.fill("#firstName", first)
        self.fill("#lastName", last)
        self.fill("#userEmail", email)
        self.fill("#age", str(age))
        self.fill("#salary", str(salary))
        self.fill("#department", department)
        self.click("#submit")

    def search(self, query: str):
        self.fill("#searchBox", query)
        return self

    def row_by_email(self, email: str):
        return self.page.locator(".rt-tbody .rt-tr-group", has_text=email)

    def assert_row_contains(self, email: str, *parts: str):
        row = self.row_by_email(email)
        expect(row).to_be_visible()
        row_text = row.inner_text()
        for p in parts:
            assert p in row_text

    def edit_row_by_email(self, email: str, **new_values):
        row = self.row_by_email(email)
        expect(row).to_be_visible()
        row.locator("span[id^='edit-record']").click()
        for field_id, value in {
            "#firstName": new_values.get("first"),
            "#lastName": new_values.get("last"),
            "#userEmail": new_values.get("email"),
            "#age": new_values.get("age"),
            "#salary": new_values.get("salary"),
            "#department": new_values.get("department"),
        }.items():
            if value is not None:
                self.fill(field_id, str(value))
        self.click("#submit")

    def delete_row_by_email(self, email: str):
        row = self.row_by_email(email)
        expect(row).to_be_visible()
        row.locator("span[id^='delete-record']").click()

    def set_rows_per_page(self, value: str):
        # usually "5", "10", "20", "25", "50", "100"
        sel = self.page.locator("select[aria-label='rows per page']")
        expect(sel).to_be_visible()
        sel.select_option(value)
        return self
