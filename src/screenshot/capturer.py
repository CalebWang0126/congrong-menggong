# src/screenshot/capturer.py
import io
import uuid
from pathlib import Path

import mss
from PIL import Image
from loguru import logger


class Screenshotter:
    MAX_SIZE_KB: int = 200

    def __init__(self, temp_dir: Path | str | None = None) -> None:
        if temp_dir is None:
            temp_dir = Path.home() / "AppData" / "Local" / "Temp" / "congrong-menggong"
        self._temp_dir = Path(temp_dir)
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        self._mss = mss.mss()

    def capture(self) -> Path:
        logger.debug("Capturing screenshot...")
        screen = self._mss.grab(self._mss.monitors[0])
        pil_image = Image.frombytes("RGB", screen.size, screen.bgra, "raw", "BGRX")

        filepath = self._temp_dir / f"screenshot_{uuid.uuid4().hex[:8]}.jpg"

        quality = 85
        while True:
            buf = io.BytesIO()
            pil_image.save(buf, format="JPEG", quality=quality)
            size_kb = buf.tell() / 1024
            if size_kb <= self.MAX_SIZE_KB or quality <= 10:
                break
            quality -= 5

        filepath.write_bytes(buf.getvalue())
        logger.info(f"Screenshot saved: {filepath} ({filepath.stat().st_size / 1024:.0f}KB)")
        return filepath

    def cleanup(self, path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
            logger.debug(f"Cleaned up: {path}")
        except OSError as e:
            logger.warning(f"Failed to clean up {path}: {e}")
