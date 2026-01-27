from pages.alerts_frames_windows.browser_windows_page import BrowserWindowsPage

def test_browser_windows_new_tab_and_window(page):
    bw = BrowserWindowsPage(page).open_page()
    bw.open_new_tab_and_check()
    bw.open_new_window_and_check()
