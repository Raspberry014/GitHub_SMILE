from pages.elements.links_page import LinksPage

def test_links_open_new_tabs(page):
    lp = LinksPage(page).open_page()
    lp.open_simple_link_new_tab()
    lp.open_dynamic_link_new_tab()

def test_links_api_responses(page):
    lp = LinksPage(page).open_page()
    cases = [
        ("created", "201"),
        ("no-content", "204"),
        ("moved", "301"),
        ("bad-request", "400"),
        ("unauthorized", "401"),
        ("forbidden", "403"),
        ("invalid-url", "404"),
    ]
    for link_id, code in cases:
        lp.click_api_link_and_assert_code(link_id, code)
