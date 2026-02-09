from pages.interactions.sortable_page import SortablePage


def test_sortable_list_drag_and_drop(page):
    sp = SortablePage(page).open_page()
    before = sp.get_list_order()
    sp.drag_item_to("One", "Six")
    after = sp.get_list_order()
    assert before != after
    assert after[0] != "One"
