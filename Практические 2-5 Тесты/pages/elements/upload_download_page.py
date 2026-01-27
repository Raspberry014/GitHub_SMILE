from pathlib import Path
from playwright.sync_api import expect
from pages.base_page import BasePage

class UploadDownloadPage(BasePage):
    PATH = "/upload-download"

    def open_page(self):
        return self.open(self.PATH)

    def upload_file(self, filepath: str):
        p = Path(filepath)
        assert p.exists(), f"File not found: {filepath}"
        self.page.set_input_files("#uploadFile", str(p))
        expect(self.page.locator("#uploadedFilePath")).to_be_visible()
        return self.page.locator("#uploadedFilePath").inner_text()

    def download_file(self, save_dir: str):
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        with self.page.expect_download() as dlinfo:
            self.page.click("#downloadButton")
        download = dlinfo.value
        suggested = download.suggested_filename
        target = Path(save_dir) / suggested
        download.save_as(str(target))
        assert target.exists() and target.stat().st_size > 0
        return str(target)
