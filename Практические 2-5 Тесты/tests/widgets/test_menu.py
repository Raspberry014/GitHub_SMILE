from pages.widgets.menu_page import MenuPage


def test_menu_nested_visibility_and_click(page):
    m = MenuPage(page).open_page()
    m.hover_main_item_2()
    m.assert_sub_items_visible()

    m.hover_sub_sub_list()
    m.assert_sub_sub_items_visible()

    m.click_sub_sub_item_2()  # should be clickable without errors
