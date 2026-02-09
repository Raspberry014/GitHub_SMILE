from playwright.sync_api import expect
from pages.base_page import BasePage


class ResizablePage(BasePage):
    PATH = "/resizable"

    def open_page(self):
        return self.open(self.PATH)

    def _drag_handle(self, box_selector: str, dx: int, dy: int):
        box = self.page.locator(box_selector)
        handle = box.locator(".react-resizable-handle-se")
        expect(handle).to_be_visible()
        hb = handle.bounding_box()
        assert hb, "Resize handle has no bounding box"
        x = hb["x"] + hb["width"] / 2
        y = hb["y"] + hb["height"] / 2
        self.page.mouse.move(x, y)
        self.page.mouse.down()
        self.page.mouse.move(x + dx, y + dy)
        self.page.mouse.up()

    def get_box_size(self, box_selector: str):
        bb = self.page.locator(box_selector).bounding_box()
        assert bb, "Box has no bounding box"
        return bb["width"], bb["height"]

    def resize_restricted(self, dx: int = 400, dy: int = 300):
        # has max/min restrictions
        self._drag_handle("#resizableBoxWithRestriction", dx, dy)

    def resize_unrestricted(self, dx: int = 200, dy: int = 140):
        self._drag_handle("#resizable", dx, dy)
