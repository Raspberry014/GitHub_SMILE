from playwright.sync_api import expect
from pages.base_page import BasePage


class SortablePage(BasePage):
    PATH = "/sortable"

    def open_page(self):
        return self.open(self.PATH)

    def list_items(self):
        # list tab is default
        return self.page.locator("#demo-tabpane-list .list-group-item")

    def get_list_order(self):
        return self.list_items().all_inner_texts()

    def drag_item_to(self, source_text: str, target_text: str):
        src = self.page.locator("#demo-tabpane-list .list-group-item", has_text=source_text)
        tgt = self.page.locator("#demo-tabpane-list .list-group-item", has_text=target_text)
        expect(src).to_be_visible()
        expect(tgt).to_be_visible()
        src.drag_to(tgt)
