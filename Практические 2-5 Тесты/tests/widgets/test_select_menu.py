from pages.widgets.select_menu_page import SelectMenuPage


def test_select_menu_single_and_multi(page):
    sm = SelectMenuPage(page).open_page()

    sm.choose_select_value("Group 1, option 1")
    sm.assert_select_value_contains("Group 1, option 1")

    sm.choose_select_one("Mrs.")
    sm.assert_select_one_contains("Mrs.")

    sm.choose_old_style_color("Purple")
    sm.assert_old_style_selected("Purple")

    sm.choose_multi_select(["Green", "Blue"])
    sm.assert_multi_select_contains("Green")
    sm.assert_multi_select_contains("Blue")

    sm.choose_standard_multi(["Volvo", "Saab"])
    sm.assert_standard_multi_selected(["Volvo", "Saab"])
