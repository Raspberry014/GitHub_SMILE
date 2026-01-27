from pages.alerts_frames_windows.alerts_page import AlertsPage

def test_alerts_all_types(page):
    a = AlertsPage(page).open_page()
    a.handle_simple_alert()
    a.handle_timer_alert()
    a.handle_confirm_ok()
    a.handle_confirm_cancel()
    a.handle_prompt("hello")
