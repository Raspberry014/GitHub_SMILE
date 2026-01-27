from pages.elements.radio_button_page import RadioButtonPage

def test_radio_buttons_yes(page):
    rb = RadioButtonPage(page).open_page()
    rb.choose_yes().assert_result("Yes")

def test_radio_buttons_impressive(page):
    rb = RadioButtonPage(page).open_page()
    rb.choose_impressive().assert_result("Impressive")

def test_radio_no_disabled(page):
    rb = RadioButtonPage(page).open_page()
    rb.assert_no_disabled()
