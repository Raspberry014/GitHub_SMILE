from faker import Faker
from pages.elements.web_tables_page import WebTablesPage

fake = Faker()

def test_web_tables_add_search_edit_delete_and_rows_per_page(page):
    wt = WebTablesPage(page).open_page()

    email = fake.email()
    first = fake.first_name()
    last = fake.last_name()

    # add
    wt.add_record(first, last, email, age=28, salary=5000, department="QA")
    wt.search(email)
    wt.assert_row_contains(email, first, last)

    # edit
    new_department = "Automation"
    wt.edit_row_by_email(email, department=new_department)
    wt.search(email)
    wt.assert_row_contains(email, new_department)

    # rows per page
    wt.set_rows_per_page("5")

    # delete
    wt.delete_row_by_email(email)
    wt.search(email)
    # After deletion, the row should disappear or show "No rows found"
    assert "No rows found" in page.locator(".rt-noData").inner_text()
