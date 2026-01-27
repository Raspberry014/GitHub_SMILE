from pages.alerts_frames_windows.modal_dialogs_page import ModalDialogsPage

def test_modal_dialogs_small_and_large(page):
    m = ModalDialogsPage(page).open_page()
    m.open_small_and_close_button()
    m.open_large_and_close_x()
