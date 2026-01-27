def remove_demoqa_banners(page):
    # DemoQA sometimes has fixed banners/iframes that block clicks.
    page.add_style_tag(content="""
    #fixedban, #adplus-anchor, iframe[id^='google_ads'], iframe[title*='Advertisement'], .adsbygoogle {
        display:none !important;
        visibility:hidden !important;
        height:0 !important;
    }
    """)
