from pages.interactions.droppable_page import DroppablePage


def test_droppable_simple(page):
    d = DroppablePage(page).open_page()
    d.open_tab("simple")
    d.drag_to_drop(d.simple_draggable(), d.simple_droppable())
    d.assert_simple_dropped()


def test_droppable_accept(page):
    d = DroppablePage(page).open_page()
    d.open_tab("accept")

    d.drag_to_drop("#droppableExample-tabpane-accept #notAcceptable", d.accept_droppable())
    d.assert_accept_text("Drop here")

    d.drag_to_drop("#droppableExample-tabpane-accept #acceptable", d.accept_droppable())
    d.assert_accept_text("Dropped!")


def test_droppable_prevent_propagation(page):
    d = DroppablePage(page).open_page()
    d.open_tab("prevent")

    d.drag_to_drop(d.prevent_dragbox(), d.prevent_inner())
    d.assert_prevent_inner_dropped()
    d.assert_prevent_outer_dropped()  # not-greedy: outer also reacts


def test_droppable_revert_draggable(page):
    d = DroppablePage(page).open_page()
    d.open_tab("revert")

    drag = d.revertable()
    bb = drag.bounding_box()
    assert bb, "no bbox for revertable"
    initial_x = bb["x"]

    d.drag_to_drop("#droppableExample-tabpane-revertable #revertable", d.droppable_revert())
    # after drop it shows dropped, then returns back
    d.assert_reverted_back(initial_x)
