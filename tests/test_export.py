"""Tests for the export pipeline, including single-file HTML bundling."""

import json
import os
import tempfile

import pytest

from preswald.utils import bundle_single_file_html


class TestBundleSingleFileHtml:
    """Tests for bundle_single_file_html."""

    def _create_export_dir(self, tmp_path):
        """Set up a minimal export directory structure."""
        export_dir = str(tmp_path / "export")
        os.makedirs(os.path.join(export_dir, "assets"))

        # index.html with script and css references
        index_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <title>Test App</title>
    <link rel="stylesheet" href="assets/main.css" />
</head>
<body>
    <div id="root"></div>
    <script type="module" src="assets/main.js"></script>
</body>
</html>"""
        with open(os.path.join(export_dir, "index.html"), "w") as f:
            f.write(index_html)

        # CSS file
        with open(os.path.join(export_dir, "assets", "main.css"), "w") as f:
            f.write("body { margin: 0; } .app { color: red; }")

        # JS file
        with open(os.path.join(export_dir, "assets", "main.js"), "w") as f:
            f.write("console.log('hello');")

        # project_fs.json
        project_fs = {
            "__entrypoint__": "app.py",
            "app.py": {"type": "text", "content": "import preswald as pw\npw.text('hello')"},
        }
        with open(os.path.join(export_dir, "project_fs.json"), "w") as f:
            json.dump(project_fs, f)

        return export_dir

    def test_produces_single_file(self, tmp_path):
        export_dir = self._create_export_dir(tmp_path)
        output_path = str(tmp_path / "output.html")

        result = bundle_single_file_html(export_dir, output_path)

        assert result == output_path
        assert os.path.exists(output_path)

    def test_inlines_css(self, tmp_path):
        export_dir = self._create_export_dir(tmp_path)
        output_path = str(tmp_path / "output.html")

        bundle_single_file_html(export_dir, output_path)

        with open(output_path) as f:
            html = f.read()

        # CSS should be inlined
        assert "<style>" in html
        assert "body { margin: 0; }" in html
        # Original link tag should be gone
        assert 'href="assets/main.css"' not in html

    def test_inlines_js(self, tmp_path):
        export_dir = self._create_export_dir(tmp_path)
        output_path = str(tmp_path / "output.html")

        bundle_single_file_html(export_dir, output_path)

        with open(output_path) as f:
            html = f.read()

        # JS should be inlined
        assert "console.log('hello');" in html
        # Original src should be gone
        assert 'src="assets/main.js"' not in html

    def test_embeds_project_fs(self, tmp_path):
        export_dir = self._create_export_dir(tmp_path)
        output_path = str(tmp_path / "output.html")

        bundle_single_file_html(export_dir, output_path)

        with open(output_path) as f:
            html = f.read()

        assert "window.__PRESWALD_PROJECT_FS" in html
        assert "__entrypoint__" in html
        assert "app.py" in html

    def test_preserves_external_urls(self, tmp_path):
        export_dir = self._create_export_dir(tmp_path)
        # Add an external URL reference to the HTML
        index_path = os.path.join(export_dir, "index.html")
        with open(index_path, "r") as f:
            html = f.read()
        html = html.replace("</head>", '<script src="https://cdn.example.com/lib.js"></script>\n</head>')
        with open(index_path, "w") as f:
            f.write(html)

        output_path = str(tmp_path / "output.html")
        bundle_single_file_html(export_dir, output_path)

        with open(output_path) as f:
            result = f.read()

        # External URL should be preserved
        assert "https://cdn.example.com/lib.js" in result

    def test_inlines_css_url_assets(self, tmp_path):
        export_dir = self._create_export_dir(tmp_path)
        # Add an image referenced by CSS
        os.makedirs(os.path.join(export_dir, "assets", "img"), exist_ok=True)
        with open(os.path.join(export_dir, "assets", "img", "bg.png"), "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)  # minimal PNG-like bytes

        # Update CSS to reference the image
        with open(os.path.join(export_dir, "assets", "main.css"), "w") as f:
            f.write("body { background: url(img/bg.png); }")

        output_path = str(tmp_path / "output.html")
        bundle_single_file_html(export_dir, output_path)

        with open(output_path) as f:
            html = f.read()

        # Image should be base64-inlined in the CSS
        assert "data:image/png;base64," in html
        assert "url(img/bg.png)" not in html

    def test_no_project_fs_still_works(self, tmp_path):
        export_dir = self._create_export_dir(tmp_path)
        os.remove(os.path.join(export_dir, "project_fs.json"))

        output_path = str(tmp_path / "output.html")
        bundle_single_file_html(export_dir, output_path)

        with open(output_path) as f:
            html = f.read()

        # Should still produce valid HTML
        assert "<html>" in html
        assert "window.__PRESWALD_PROJECT_FS" not in html
