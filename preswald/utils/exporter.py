import os

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def export_app_to_pdf(output_path: str, port: int = 8501):
    """
    Launches the running Preswald app in a headless browser and exports it to PDF.
    Specifically waits for Plotly charts to finish rendering.

    Args:
        output_path (str): The destination path for the PDF file.
        port (int): The port the app is running on (default: 8501).
    """
    url = f"http://localhost:{port}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 2000},
            device_scale_factor=2,
        )
        page = context.new_page()

        print(f"📄 Visiting {url} ...")
        page.goto(url, wait_until="networkidle")

        # Emulate screen media for layout fidelity
        page.emulate_media(media="screen")

        # Wait for Plotly charts to fully render
        try:
            print("⏳ Waiting for Plotly chart containers...")
            page.wait_for_selector("div.js-plotly-plot", timeout=40000)

            charts = page.query_selector_all("div.js-plotly-plot")
            for i, chart in enumerate(charts):
                print(f"🧪 Waiting for chart {i + 1} to render...")
                chart.wait_for_selector("svg", timeout=30000)

            page.wait_for_timeout(2000)  # Extra safety buffer
            print("✅ All detected charts appear rendered.")
        except PlaywrightTimeoutError:
            print("⚠️ Timeout: Some charts may not have rendered fully.")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        page.pdf(path=output_path, format="A4", print_background=True)

        print(f"✅ PDF saved to {output_path}")
        browser.close()
