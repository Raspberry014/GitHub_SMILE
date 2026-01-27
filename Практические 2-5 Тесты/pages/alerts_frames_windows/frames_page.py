from playwright.sync_api import expect
from pages.base_page import BasePage

class FramesPage(BasePage):
    PATH = "/frames"

    def open_page(self):
        return self.open(self.PATH)

    def assert_big_frame_text(self):
        t = self.page.frame_locator("#frame1").locator("#sampleHeading")
        expect(t).to_have_text("This is a sample page")

    def assert_small_frame_text(self):
        t = self.page.frame_locator("#frame2").locator("#sampleHeading")
        expect(t).to_have_text("This is a sample page")
