from pages.widgets.tool_tips_page import ToolTipsPage


def test_tool_tips_button_and_input(page):
    tt = ToolTipsPage(page).open_page()
    tt.hover_button()
    tt.assert_tooltip_text("You hovered over the Button")

    tt.hover_input()
    tt.assert_tooltip_text("You hovered over the text field")
