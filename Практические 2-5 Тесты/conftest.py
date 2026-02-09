import json
import os
import logging
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError, Error as PWError
from utils.ui_fixes import remove_demoqa_banners


def _to_bool(v: str) -> bool:
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}

def load_settings():
    with open("config/settings.json", "r", encoding="utf-8") as f:
        s = json.load(f)
    # Env overrides
    if os.getenv("BASE_URL"):
        s["base_url"] = os.environ["BASE_URL"]
    if os.getenv("BROWSER"):
        s["browser"] = os.environ["BROWSER"]
    if os.getenv("HEADLESS") is not None:
        s["headless"] = _to_bool(os.environ["HEADLESS"])
    if os.getenv("TIMEOUT_MS"):
        s["timeout_ms"] = int(os.environ["TIMEOUT_MS"])
    if os.getenv("RECORD_VIDEO") is not None:
        s["record_video"] = _to_bool(os.environ["RECORD_VIDEO"])
    return s

@pytest.fixture(scope="session")
def settings():
    return load_settings()

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance, settings):
    bt = getattr(playwright_instance, settings["browser"])
    b = bt.launch(headless=settings["headless"])
    yield b
    b.close()

@pytest.fixture()
def context(browser, settings):
    Path("artifacts/reports").mkdir(parents=True, exist_ok=True)
    Path("artifacts/screenshots").mkdir(parents=True, exist_ok=True)
    Path("artifacts/downloads").mkdir(parents=True, exist_ok=True)
    Path("artifacts/uploads").mkdir(parents=True, exist_ok=True)
    Path("artifacts/videos").mkdir(parents=True, exist_ok=True)

    record_video = settings.get("record_video", False)

    ctx = browser.new_context(
        base_url=settings["base_url"],
        accept_downloads=True,
        record_video_dir="artifacts/videos" if record_video else None
    )
    ctx.set_default_timeout(settings["timeout_ms"])

    # ✅ ВАЖНО: add_init_script ДО yield
    ctx.add_init_script("""
    (() => {
      const css = `
        #fixedban, .fixedban,
        #adplus-anchor, [id^="adplus-"],
        iframe[id^="google_ads_iframe_"],
        iframe[src*="doubleclick"],
        ins.adsbygoogle, .adsbygoogle
        { display:none !important; pointer-events:none !important; }
      `;
      const style = document.createElement('style');
      style.setAttribute('data-demoqa-fix', '1');
      style.textContent = css;
      document.documentElement.appendChild(style);
    })();
    """)

    yield ctx
    ctx.close()


@pytest.fixture()
def page(context):
    p = context.new_page()
    p.set_viewport_size({"width": 1366, "height": 900})
    remove_demoqa_banners(p)
    yield p
    p.close()

# --- screenshot on failure (SAFE)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when != "call" or not rep.failed:
        return

    page = item.funcargs.get("page")
    if not page:
        return

    Path("artifacts/screenshots").mkdir(parents=True, exist_ok=True)
    path = Path("artifacts/screenshots") / f"{item.name}.png"

    try:
        page.screenshot(path=str(path), full_page=False, timeout=30000)
    except (PWTimeoutError, PWError, Exception):
        pass



# --- logging (per worker) ---
def pytest_configure(config):
    Path("artifacts/logs").mkdir(parents=True, exist_ok=True)
    worker = os.getenv("PYTEST_XDIST_WORKER", "main")
    log_file = Path("artifacts/logs") / f"run_{worker}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
