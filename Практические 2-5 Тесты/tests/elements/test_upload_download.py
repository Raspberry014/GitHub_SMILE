from pathlib import Path
from pages.elements.upload_download_page import UploadDownloadPage

def test_upload_file(page):
    # create a small file to upload
    upload_path = Path("artifacts/uploads/test_upload.txt")
    upload_path.write_text("hello demoqa", encoding="utf-8")

    ud = UploadDownloadPage(page).open_page()
    uploaded_text = ud.upload_file(str(upload_path))
    assert upload_path.name in uploaded_text

def test_download_file(page):
    ud = UploadDownloadPage(page).open_page()
    saved = ud.download_file("artifacts/downloads")
    assert Path(saved).exists()
