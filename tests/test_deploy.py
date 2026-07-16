import tempfile
from pathlib import Path

import pytest

from preswald.deploy import GCP_SERVICE_NAME_MAX_LENGTH, get_container_name


def _write_toml_project(tmp_path: Path, slug: str) -> Path:
    script_path = tmp_path / "hello.py"
    script_path.write_text("")
    (tmp_path / "preswald.toml").write_text(
        f'[project]\nslug = "{slug}"\nport = 8501\n'
    )
    return script_path


def test_get_container_name_stays_under_gcp_limit():
    # A long-but-valid project slug used to produce a container name past
    # Cloud Run's <50 char service_id limit once the "preswald-app-" prefix
    # was added, causing `CreateServiceRequest.service_id` violations (#659).
    long_slug = "a-very-descriptive-project-slug-for-an-org-1744321134"
    with tempfile.TemporaryDirectory() as tmp:
        script_path = _write_toml_project(Path(tmp), long_slug)
        container_name = get_container_name(str(script_path))

    assert len(container_name) <= GCP_SERVICE_NAME_MAX_LENGTH
    assert not container_name.endswith("-")
    assert container_name.startswith("preswald-app-")


def test_get_container_name_short_slug_unaffected():
    with tempfile.TemporaryDirectory() as tmp:
        script_path = _write_toml_project(Path(tmp), "zwbq")
        container_name = get_container_name(str(script_path))

    assert container_name == "preswald-app-zwbq"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
