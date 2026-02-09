from pages.widgets.tabs_page import TabsPage


def test_tabs_switch_content(page):
    t = TabsPage(page).open_page()
    t.click_tab("What")
    t.assert_tab_content_visible("What", "printing and typesetting")
    t.click_tab("Origin")
    t.assert_tab_content_visible("Origin", "Contrary to popular belief")
    t.click_tab("Use")
    t.assert_tab_content_visible("Use", "established fact")
    t.assert_more_disabled()
