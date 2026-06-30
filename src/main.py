# src/main.py
"""从容猛攻助手 — Entry point."""

from __future__ import annotations

import sys
import threading
from pathlib import Path

from loguru import logger

from src.config.manager import ConfigManager
from src.monitor.matcher import MsgMatcher
from src.monitor.poller import Monitor
from src.reply.engine import ReplyEngine
from src.screenshot.capturer import Screenshotter
from src.utils.wechat_uia import WeChatUIA

# Configure loguru
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
)
logger.add(
    Path.home() / "AppData" / "Roaming" / "congrong-menggong" / "app.log",
    rotation="5 MB",
    retention="3 days",
    level="DEBUG",
)


def main() -> None:
    logger.info("Starting 从容猛攻助手...")

    # Init modules
    config = ConfigManager()
    config.load()

    wechat = WeChatUIA(window_title=config.get("wechat_window_title", "微信"))
    matcher = MsgMatcher(config.get("targets", []))
    screenshotter = Screenshotter()
    monitor = Monitor(wechat, matcher, config)
    reply_engine = ReplyEngine(wechat, screenshotter, config)

    # Check WeChat availability
    if not wechat.is_available():
        logger.warning(
            "微信未运行或未登录！请先打开并登录微信 PC 客户端，然后重启本程序。"
        )

    # Start GUI
    from src.gui.app import create_app

    # Update matcher when config targets change
    matcher.update_targets(config.get("targets", []))

    # Optional: system tray in a daemon thread
    try:
        from src.gui.tray import create_tray
        import asyncio

        loop = asyncio.get_event_loop()

        def on_exit():
            logger.info("Exiting...")
            if monitor.is_running:
                loop.call_soon_threadsafe(monitor.stop)
            import os
            os._exit(0)

        # Safe wrapper for tray to start/stop monitor from background thread
        def tray_toggle_monitor(*args):
            if monitor.is_running:
                loop.call_soon_threadsafe(monitor.stop)
            else:
                loop.call_soon_threadsafe(monitor.start, tray_on_message)

        def tray_on_message(msg: dict):
            # In tray-only mode, log the message
            logger.info(f"[Tray] New message from {msg.get('sender')}")

        tray_thread = threading.Thread(
            target=create_tray,
            args=(config, monitor, lambda: None, on_exit, tray_toggle_monitor),
            daemon=True,
        )
        tray_thread.start()
    except Exception as e:
        logger.warning(f"System tray unavailable: {e}")

    # Launch NiceGUI
    create_app(config, monitor, reply_engine)

    import nicegui
    nicegui.ui.run(
        title="从容猛攻助手",
        native=True,
        window_size=(480, 720),
        reload=False,
    )


if __name__ == "__main__":
    main()
