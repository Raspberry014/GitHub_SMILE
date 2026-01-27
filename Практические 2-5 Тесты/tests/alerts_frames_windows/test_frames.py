from pages.alerts_frames_windows.frames_page import FramesPage

def test_frames_big_and_small(page):
    f = FramesPage(page).open_page()
    f.assert_big_frame_text()
    f.assert_small_frame_text()
