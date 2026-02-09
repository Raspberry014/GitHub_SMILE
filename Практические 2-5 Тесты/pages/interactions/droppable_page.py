from playwright.sync_api import expect
from pages.base_page import BasePage


class DroppablePage(BasePage):
    PATH = "/droppable"

    def open_page(self):
        return self.open(self.PATH)

    def open_tab(self, tab_name: str):
        name = tab_name.strip().lower()
        mapping = {
            "simple": "#droppableExample-tab-simple",
            "accept": "#droppableExample-tab-accept",
            "prevent": "#droppableExample-tab-preventPropogation",
            "revert": "#droppableExample-tab-revertable",
        }
        self.page.locator(mapping[name]).click()

    def drag_to_drop(self, draggable_selector: str, droppable_selector: str):
        src = self.page.locator(draggable_selector)
        tgt = self.page.locator(droppable_selector)
        expect(src).to_be_visible()
        expect(tgt).to_be_visible()
        src.drag_to(tgt)

    # --- Simple
    def simple_draggable(self):
        return "#droppableExample-tabpane-simple #draggable"

    def simple_droppable(self):
        return "#droppableExample-tabpane-simple #droppable"

    def assert_simple_dropped(self):
        expect(self.page.locator(self.simple_droppable())).to_contain_text("Dropped!")

    # --- Accept
    def accept_droppable(self):
        return "#droppableExample-tabpane-accept #droppable"

    def assert_accept_text(self, expected: str):
        expect(self.page.locator(self.accept_droppable())).to_contain_text(expected)

    # --- Prevent propagation (not greedy section)
    def prevent_dragbox(self):
        return "#droppableExample-tabpane-preventPropogation #dragBox"

    def prevent_outer(self):
        return "#droppableExample-tabpane-preventPropogation #notGreedyDropBox"

    def prevent_inner(self):
        return "#droppableExample-tabpane-preventPropogation #notGreedyInnerDropBox"

    def assert_prevent_inner_dropped(self):
        expect(self.page.locator(self.prevent_inner())).to_contain_text("Dropped!")

    def assert_prevent_outer_dropped(self):
        expect(self.page.locator(self.prevent_outer())).to_contain_text("Dropped!")

    # --- Revert
    def revertable(self):
        return self.page.locator("#droppableExample-tabpane-revertable #revertable")

    def droppable_revert(self):
        return "#droppableExample-tabpane-revertable #droppable"

    def assert_reverted_back(self, initial_x: float, tolerance: float = 6.0):
        loc = self.revertable()

        def _x():
            bb = loc.bounding_box()
            return bb["x"] if bb else None

        # wait until it comes back close to initial position
        expect.poll(_x, timeout=7000).to_be_close_to(initial_x, abs=tolerance)
