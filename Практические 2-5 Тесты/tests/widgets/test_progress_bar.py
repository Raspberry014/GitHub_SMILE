from pages.widgets.progress_bar_page import ProgressBarPage

def test_progress_bar(page):
    pb = ProgressBarPage(page).open_page()
    pb.start()
    pb.wait_until("50")
    pb.reset()
