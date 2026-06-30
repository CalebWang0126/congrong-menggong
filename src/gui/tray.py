from __future__ import annotations

import threading
from typing import Callable

from PIL import Image, ImageDraw
from loguru import logger

try:
    import pystray
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False


def _make_icon_image() -> Image.Image:
    """Generate a simple 64x64 tray icon."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Green circle
    draw.ellipse([4, 4, 60, 60], fill=(76, 175, 80))
    # White gamepad-ish shape
    draw.rectangle([20, 22, 44, 42], fill=(255, 255, 255))
    draw.ellipse([14, 18, 28, 32], fill=(255, 255, 255))
    draw.ellipse([36, 18, 50, 32], fill=(255, 255, 255))
    return img


def create_tray(
    config,
    monitor,
    on_show: Callable[[], None],
    on_exit: Callable[[], None],
) -> None:
    """Create and run a system tray icon. Blocks the current thread."""
    if not HAS_PYSTRAY:
        logger.warning("pystray not installed, skipping system tray")
        return

    icon = pystray.Icon(
        "congrong-menggong",
        _make_icon_image(),
        "从容猛攻助手",
    )

    def _show():
        on_show()

    def _toggle_monitor():
        if monitor.is_running:
            monitor.stop()
        else:
            monitor.start(lambda msg: None)

    def _exit():
        if monitor.is_running:
            monitor.stop()
        icon.stop()
        on_exit()

    icon.menu = pystray.Menu(
        pystray.MenuItem("显示主窗口", _show, default=True),
        pystray.MenuItem("开始/停止监听", _toggle_monitor),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("退出", _exit),
    )

    icon.run()
