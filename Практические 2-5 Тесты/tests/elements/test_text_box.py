from utils.data_loader import load_json
from pages.elements.text_box_page import TextBoxPage

def test_text_box_happy_path(page):
    data = load_json("data/text_box.json")
    tb = TextBoxPage(page).open_page()
    tb.fill_form(data["full_name"], data["email"], data["current_address"], data["permanent_address"])
    tb.assert_output(data["full_name"], data["email"], data["current_address"], data["permanent_address"])

def test_text_box_invalid_email(page):
    tb = TextBoxPage(page).open_page()
    tb.fill_form("Test", "not-an-email", "A", "B")
    tb.assert_invalid_email()
