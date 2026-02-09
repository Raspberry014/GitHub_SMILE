from pages.interactions.resizable_page import ResizablePage


def test_resizable_restricted_and_unrestricted(page):
    r = ResizablePage(page).open_page()

    # restricted box
    w1, h1 = r.get_box_size("#resizableBoxWithRestriction")
    r.resize_restricted(dx=800, dy=800)
    w2, h2 = r.get_box_size("#resizableBoxWithRestriction")
    assert w2 >= w1 and h2 >= h1
    # max constraints on demoqa
    assert w2 <= 505 and h2 <= 305

    # unrestricted box
    w3, h3 = r.get_box_size("#resizable")
    r.resize_unrestricted(dx=200, dy=150)
    w4, h4 = r.get_box_size("#resizable")
    assert w4 > w3 and h4 > h3
