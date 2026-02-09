from pages.interactions.selectable_page import SelectablePage


def test_selectable_single_and_multi(page):
    s = SelectablePage(page).open_page()

    first = "Cras justo odio"
    second = "Dapibus ac facilisis in"

    s.click_item(first)
    s.assert_selected(first)

    s.click_item(second, ctrl=True)
    s.assert_selected(first)
    s.assert_selected(second)
