from pathlib import Path


def test_logo_assets_exist_and_app_references_repo_local_paths():
    root = Path(__file__).resolve().parents[1]
    logo = root / "app" / "assets" / "veritasclin-field-logo.png"
    mark = root / "app" / "assets" / "veritasclin-field-mark.png"
    app = root / "app" / "streamlit_app.py"

    assert logo.exists()
    assert mark.exists()
    source = app.read_text(encoding="utf-8")
    assert "veritasclin-field-logo.png" in source
    assert "veritasclin-field-mark.png" in source
    assert "/Users/sthef/Downloads" not in source
