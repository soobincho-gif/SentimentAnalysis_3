from __future__ import annotations

import re
import socket
import time
from multiprocessing import Process
from pathlib import Path
from urllib.request import urlopen

import pytest
from PIL import Image

from packages.core.models.evaluation import EvaluationReport
from packages.core.models.scene import SceneObservation
from packages.core.models.sequence import SequenceMemory
from packages.core.models.story import StoryResult
from submission.app import build_ui
from submission.styles import APP_CSS, APP_HEAD

selenium = pytest.importorskip("selenium")

from selenium import webdriver  # noqa: E402
from selenium.webdriver.chrome.options import Options  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def _available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def _stub_result() -> StoryResult:
    return StoryResult(
        title="Browser Verified Story",
        story_text="A grounded story appears after the real browser click.",
        original_scene_observations=[
            SceneObservation(
                image_id=1,
                entities=["dog"],
                setting="park",
                actions=["standing"],
            )
        ],
        scene_observations=[
            SceneObservation(
                image_id=1,
                entities=["dog"],
                setting="park",
                actions=["standing"],
            )
        ],
        sequence_memory=SequenceMemory(
            recurring_entities=["dog"],
            setting_progression=["park"],
        ),
        evaluation_report=EvaluationReport(
            grounding_score=0.93,
            coherence_score=0.91,
            redundancy_score=0.92,
            sentiment_fit_score=0.90,
            readability_score=0.89,
            flags=[],
            summary="Passed",
        ),
        sentence_alignment=[[1]],
        grounding_notes=["dog remains visible"],
    )


def _serve_stubbed_app(
    port: int,
    delay_seconds: float = 0.0,
    fail_message: str | None = None,
) -> None:
    import submission.controller as controller

    class DummyPipeline:
        def run(self, request):  # type: ignore[no-untyped-def]
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            if fail_message is not None:
                raise RuntimeError(fail_message)
            return _stub_result()

    controller.build_pipeline = lambda: DummyPipeline()
    controller.persist_uploaded_images = lambda paths: list(paths)
    controller.cleanup_persisted_images = lambda paths: None

    app = build_ui()
    app.launch(
        server_name="127.0.0.1",
        server_port=port,
        prevent_thread_lock=True,
        quiet=True,
        css=APP_CSS,
        head=APP_HEAD,
        footer_links=[],
    )
    while True:
        time.sleep(1)


@pytest.fixture(scope="module")
def stubbed_submission_url() -> str:
    port = _available_port()
    process = Process(target=_serve_stubbed_app, args=(port,), daemon=True)
    process.start()

    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2):
                break
        except Exception:
            time.sleep(1)
    else:
        process.terminate()
        process.join(timeout=5)
        pytest.fail(f"Timed out waiting for stubbed Gradio app at {url}")

    yield url

    process.terminate()
    process.join(timeout=10)


@pytest.fixture()
def delayed_submission_url() -> str:
    port = _available_port()
    process = Process(target=_serve_stubbed_app, args=(port, 3.0), daemon=True)
    process.start()

    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2):
                break
        except Exception:
            time.sleep(1)
    else:
        process.terminate()
        process.join(timeout=5)
        pytest.fail(f"Timed out waiting for delayed Gradio app at {url}")

    yield url

    process.terminate()
    process.join(timeout=10)


@pytest.fixture()
def failing_submission_url() -> str:
    port = _available_port()
    process = Process(
        target=_serve_stubbed_app,
        args=(port, 2.0, "Couldn't generate a story yet."),
        daemon=True,
    )
    process.start()

    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2):
                break
        except Exception:
            time.sleep(1)
    else:
        process.terminate()
        process.join(timeout=5)
        pytest.fail(f"Timed out waiting for failing Gradio app at {url}")

    yield url

    process.terminate()
    process.join(timeout=10)


@pytest.fixture()
def chrome_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1440,1100")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    yield driver
    driver.quit()


def _make_image(path: Path) -> str:
    Image.new("RGB", (180, 120), color=(220, 180, 150)).save(path)
    return str(path)


def test_browser_generate_story_renders_visible_result(
    stubbed_submission_url: str,
    chrome_driver,
    tmp_path: Path,
) -> None:
    image_path = _make_image(tmp_path / "upload.png")
    wait = WebDriverWait(chrome_driver, 60)

    chrome_driver.get(stubbed_submission_url)
    file_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
    )
    file_input.send_keys(image_path)

    generate_button = wait.until(EC.element_to_be_clickable((By.ID, "generate-button")))
    generate_button.click()

    story_title = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".story-title")))
    status_banner = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".status-banner"))
    )

    assert story_title.text == "Browser Verified Story"
    assert "Story ready" in status_banner.text


def test_browser_button_availability_follows_prerequisites(
    stubbed_submission_url: str,
    chrome_driver,
    tmp_path: Path,
) -> None:
    image_path = _make_image(tmp_path / "stateful-upload.png")
    wait = WebDriverWait(chrome_driver, 60)

    chrome_driver.get(stubbed_submission_url)
    wait.until(EC.presence_of_element_located((By.ID, "generate-button")))

    assert chrome_driver.find_element(By.ID, "generate-button").get_attribute("disabled") is not None
    assert chrome_driver.find_element(By.ID, "regenerate-button").get_attribute("disabled") is not None
    assert chrome_driver.find_element(By.ID, "strict-regenerate-button").get_attribute("disabled") is not None
    assert chrome_driver.find_element(By.ID, "corrected-generate-button").get_attribute("disabled") is not None
    assert (
        chrome_driver.find_element(By.ID, "corrected-strict-generate-button").get_attribute("disabled")
        is not None
    )
    assert "Generate a story first" in chrome_driver.find_element(By.CSS_SELECTOR, ".action-guidance-shell").text

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))).send_keys(
        image_path
    )
    wait.until(
        lambda driver: driver.find_element(By.ID, "generate-button").get_attribute("disabled")
        is None
    )
    assert chrome_driver.find_element(By.ID, "regenerate-button").get_attribute("disabled") is not None
    assert chrome_driver.find_element(By.ID, "corrected-generate-button").get_attribute("disabled") is not None

    chrome_driver.find_element(By.ID, "generate-button").click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".story-title")))
    wait.until(
        lambda driver: driver.find_element(By.ID, "regenerate-button").get_attribute("disabled")
        is None
    )
    wait.until(
        lambda driver: driver.find_element(By.ID, "strict-regenerate-button").get_attribute("disabled")
        is None
    )
    assert chrome_driver.find_element(By.ID, "corrected-generate-button").get_attribute("disabled") is not None

    analysis_tab = wait.until(
        lambda driver: (
            tabs if len(tabs := driver.find_elements(By.CSS_SELECTOR, '#results-tabs [role="tab"]')) >= 2 else False
        )
    )[1]
    chrome_driver.execute_script("arguments[0].click();", analysis_tab)
    subject_input = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//label[contains(., 'Correct main subject')]/following::textarea[1]")
        )
    )
    subject_input.clear()
    subject_input.send_keys("dog")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Save correction']"))).click()
    wait.until(
        lambda driver: driver.find_element(By.ID, "corrected-generate-button").get_attribute("disabled")
        is None
    )
    wait.until(
        lambda driver: driver.find_element(By.ID, "corrected-strict-generate-button").get_attribute("disabled")
        is None
    )


def test_browser_shows_processing_timer_and_restores_generate_button(
    delayed_submission_url: str,
    chrome_driver,
    tmp_path: Path,
) -> None:
    image_path = _make_image(tmp_path / "delayed-upload.png")
    wait = WebDriverWait(chrome_driver, 60)

    chrome_driver.get(delayed_submission_url)
    file_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
    )
    file_input.send_keys(image_path)

    generate_button = wait.until(EC.element_to_be_clickable((By.ID, "generate-button")))
    generate_button.click()

    wait.until(
        lambda driver: "Generating story..."
        in driver.find_element(By.CSS_SELECTOR, ".status-banner").text
    )
    wait.until(
        lambda driver: driver.find_element(By.ID, "generate-button").get_attribute("disabled")
        is not None
    )

    time.sleep(1.3)
    processing_text = chrome_driver.find_element(By.CSS_SELECTOR, ".status-banner").text
    assert re.search(r"Processing\.\.\. [12]s", processing_text)

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".story-title")))
    wait.until(
        lambda driver: driver.find_element(By.ID, "generate-button").get_attribute("disabled")
        is None
    )
    assert chrome_driver.find_element(By.ID, "generate-button").text == "Generate Story"
    assert "Story ready" in chrome_driver.find_element(By.CSS_SELECTOR, ".status-banner").text


def test_browser_failure_replaces_processing_state_without_conflict(
    failing_submission_url: str,
    chrome_driver,
    tmp_path: Path,
) -> None:
    image_path = _make_image(tmp_path / "failing-upload.png")
    wait = WebDriverWait(chrome_driver, 60)

    chrome_driver.get(failing_submission_url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))).send_keys(
        image_path
    )
    wait.until(EC.element_to_be_clickable((By.ID, "generate-button"))).click()

    wait.until(
        lambda driver: "Generating story..."
        in driver.find_element(By.CSS_SELECTOR, ".status-banner").text
    )
    wait.until(
        lambda driver: "We hit a problem before the story could be generated"
        in driver.find_element(By.CSS_SELECTOR, ".status-banner").text
    )

    status_text = chrome_driver.find_element(By.CSS_SELECTOR, ".status-banner").text
    assert "Generating story..." not in status_text
    assert "Couldn't generate a story yet." in status_text
    assert chrome_driver.find_element(By.ID, "generate-button").get_attribute("disabled") is None


def test_browser_narrow_layout_stacks_sections_cleanly(
    stubbed_submission_url: str,
    chrome_driver,
) -> None:
    chrome_driver.set_window_size(1200, 1100)
    wait = WebDriverWait(chrome_driver, 60)

    chrome_driver.get(stubbed_submission_url)
    input_column = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".workspace-input-column"))
    )
    result_column = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".workspace-result-column"))
    )

    assert abs(result_column.rect["x"] - input_column.rect["x"]) <= 5
    assert result_column.rect["y"] > input_column.rect["y"] + 100
    assert abs(result_column.rect["width"] - input_column.rect["width"]) <= 5
