from __future__ import annotations

import time
from pathlib import Path

from loguru import logger

from src.config.manager import ConfigManager
from src.screenshot.capturer import Screenshotter
from src.utils.wechat_uia import WeChatUIA


class ReplyEngine:
    """Executes reply actions: text + optional screenshot."""

    MIN_INTERVAL: float = 1.5  # seconds between sends (anti-rate-limit)

    def __init__(
        self,
        wechat: WeChatUIA,
        screenshotter: Screenshotter,
        config: ConfigManager,
    ) -> None:
        self._wechat = wechat
        self._screenshotter = screenshotter
        self._config = config
        self._last_send_time: float = 0.0

    def _wait_interval(self) -> None:
        elapsed = time.monotonic() - self._last_send_time
        if elapsed < self.MIN_INTERVAL:
            time.sleep(self.MIN_INTERVAL - elapsed)

    def send(
        self,
        contact_name: str,
        text: str,
        with_screenshot: bool | None = None,
    ) -> bool:
        """Send a reply to `contact_name`. Retries once on failure. Returns True on success."""
        if not text.strip():
            logger.warning("Empty text, skipping send")
            return False

        if with_screenshot is None:
            with_screenshot = self._config.get("screenshot", False)

        self._wait_interval()

        # Capture screenshot before attempting send (don't retry this part)
        screenshot_path: Path | None = None
        if with_screenshot:
            try:
                screenshot_path = self._screenshotter.capture()
            except Exception as e:
                logger.error(f"Screenshot failed: {e}")

        # Try send with one retry
        for attempt in (1, 2):
            if not self._wechat.open_chat(contact_name):
                if attempt == 1:
                    logger.warning(f"Retry {attempt}: could not open chat for {contact_name}")
                    time.sleep(1.0)
                    continue
                logger.error(f"Could not open chat for {contact_name} after retry")
                return False

            if not self._wechat.send_text(text):
                if attempt == 1:
                    logger.warning(f"Retry {attempt}: failed to send text")
                    time.sleep(1.0)
                    continue
                logger.error("Failed to send text after retry")
                return False

            # Success on this attempt
            break

        # Send screenshot if we have one
        if screenshot_path:
            success = self._wechat.send_image(screenshot_path)
            self._screenshotter.cleanup(screenshot_path)
            if not success:
                logger.warning("Text sent but image failed")

        self._last_send_time = time.monotonic()
        return True
