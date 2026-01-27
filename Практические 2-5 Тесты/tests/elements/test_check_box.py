from pages.elements.check_box_page import CheckBoxPage

def test_check_box_expand_collapse(page):
    cb = CheckBoxPage(page).open_page()
    cb.expand_all()
    cb.collapse_all()

def test_check_box_select_child(page):
    cb = CheckBoxPage(page).open_page().expand_all()
    cb.select_child_notes()
    cb.assert_result_contains("notes")

def test_check_box_select_parent_selects_children(page):
    cb = CheckBoxPage(page).open_page().expand_all()
    cb.select_parent_home()
    # Example tokens that often appear when selecting Home
    cb.assert_result_contains("home")
