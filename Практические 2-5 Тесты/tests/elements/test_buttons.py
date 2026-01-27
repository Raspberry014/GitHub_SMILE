from pages.elements.buttons_page import ButtonsPage

def test_buttons_clicks(page):
    b = ButtonsPage(page).open_page()
    b.double_click()
    b.right_click()
    b.dynamic_click()
    b.assert_messages()
