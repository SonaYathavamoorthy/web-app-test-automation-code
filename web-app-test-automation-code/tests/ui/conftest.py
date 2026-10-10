"""Starts the Streamlit app as a real server so Playwright tests a real browser session."""
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[2] / "sut" / "src" / "app.py"


def _free_port():
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def app_url():
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(APP), "--server.headless", "true",
         "--server.port", str(port), "--browser.gatherUsageStats", "false"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://localhost:{port}"
    for _ in range(60):
        try:
            if urllib.request.urlopen(url + "/_stcore/health", timeout=1).read() == b"ok":
                break
        except Exception:
            time.sleep(0.5)
    else:
        proc.kill()
        pytest.fail("Streamlit app did not start within 30s")
    yield url
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture
def app(page, app_url):
    page.goto(app_url)
    page.wait_for_selector("h1", timeout=20000)
    return page


def set_slider(page, label, target):
    """Move a Streamlit slider to `target` using the keyboard (the way a user without a mouse would)."""
    s = page.locator(f"input[type=range][aria-label='{label}']")
    s.focus()
    for _ in range(200):
        cur = int(float(s.input_value()))
        if cur == target:
            return
        s.press("ArrowRight" if cur < target else "ArrowLeft")
    raise AssertionError(f"could not reach {target} on slider {label!r}")


def choose_gender(page, name):
    page.get_by_label("Gender").click()
    page.get_by_role("option", name=name, exact=True).click()
    page.wait_for_timeout(800)


def predict_and_read(page):
    page.get_by_role("button", name="Predict readmission risk").click()
    page.wait_for_selector("[data-testid=stMetric]", timeout=15000)
    text = page.locator("[data-testid=stMetricValue]").inner_text()
    return float(text.strip("%")) / 100
