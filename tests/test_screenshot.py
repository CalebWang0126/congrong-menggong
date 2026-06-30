# tests/test_screenshot.py
import tempfile
from pathlib import Path
from src.screenshot.capturer import Screenshotter


class TestScreenshotter:
    def test_capture_returns_existing_file(self):
        """capture() returns a Path to an existing JPEG file."""
        with tempfile.TemporaryDirectory() as tmp:
            sc = Screenshotter(temp_dir=tmp)
            filepath = sc.capture()
            assert isinstance(filepath, Path)
            assert filepath.exists()
            assert filepath.suffix == ".jpg"
            assert filepath.stat().st_size > 0

    def test_capture_file_is_small_enough(self):
        """capture() output is <= 300KB (let 200KB target have some slack in test)."""
        with tempfile.TemporaryDirectory() as tmp:
            sc = Screenshotter(temp_dir=tmp)
            filepath = sc.capture()
            size_kb = filepath.stat().st_size / 1024
            assert size_kb < 300, f"File too large: {size_kb:.0f}KB"

    def test_cleanup_removes_file(self):
        """cleanup() deletes the captured file."""
        with tempfile.TemporaryDirectory() as tmp:
            sc = Screenshotter(temp_dir=tmp)
            filepath = sc.capture()
            assert filepath.exists()
            sc.cleanup(filepath)
            assert not filepath.exists()

    def test_cleanup_on_nonexistent_file_does_not_raise(self):
        """cleanup() on a missing file is a no-op."""
        with tempfile.TemporaryDirectory() as tmp:
            sc = Screenshotter(temp_dir=tmp)
            sc.cleanup(Path(tmp) / "nonexistent.jpg")  # should not raise

    def test_temp_dir_is_created_if_missing(self):
        """Constructor creates the temp directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "deeply" / "nested" / "screenshots"
            sc = Screenshotter(temp_dir=nested)
            assert nested.exists()
            assert nested.is_dir()
