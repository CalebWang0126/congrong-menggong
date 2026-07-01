# src/main.py
"""从容猛攻助手 — Entry point."""

from __future__ import annotations

import sys
import threading
import traceback
from pathlib import Path

# ── Crash log ─────────────────────────────
CRASH_LOG = Path(__file__).resolve().parent.parent / "crash.log"


def _crash_handler(exc_type, exc_value, exc_tb):
    """Last-resort crash handler — writes stack trace to crash.log."""
    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        CRASH_LOG.write_text(tb_text, encoding="utf-8")
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _crash_handler

# ── Logging setup ─────────────────────────
from loguru import logger  # noqa: E402

LOG_DIR = Path.home() / "AppData" / "Roaming" / "congrong-menggong"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
)
logger.add(
    LOG_DIR / "app.log",
    rotation="5 MB",
    retention="3 days",
    level="DEBUG",
)

# ── Imports ───────────────────────────────
from src.config.manager import ConfigManager  # noqa: E402
from src.monitor.matcher import MsgMatcher  # noqa: E402
from src.monitor.poller import Monitor  # noqa: E402
from src.reply.engine import ReplyEngine  # noqa: E402
from src.screenshot.capturer import Screenshotter  # noqa: E402
from src.utils.wechat_uia import WeChatUIA  # noqa: E402


def main() -> None:
    logger.info("Starting 从容猛攻助手...")

    try:
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

        matcher.update_targets(config.get("targets", []))

        tray_toggle_requested = threading.Event()

        # Optional: system tray in a daemon thread
        try:
            from src.gui.tray import create_tray  # noqa: E402

            def on_exit():
                logger.info("Exiting...")
                if monitor.is_running:
                    monitor.stop()
                import os
                os._exit(0)

            def tray_toggle_monitor(*args):
                tray_toggle_requested.set()

            tray_thread = threading.Thread(
                target=create_tray,
                args=(config, monitor, lambda: None, on_exit, tray_toggle_monitor),
                daemon=True,
            )
            tray_thread.start()
        except Exception as e:
            logger.warning(f"System tray unavailable: {e}")

        # Launch NiceGUI
        from src.gui.app import create_app  # noqa: E402
        create_app(config, monitor, reply_engine, tray_toggle_requested)

        # Check native window support
        use_native = True
        try:
            import webview  # noqa: F401
        except ImportError:
            logger.warning(
                "pywebview not available. "
                "Install Microsoft Edge WebView2 Runtime, "
                "or open http://localhost:8080 in your browser."
            )
            use_native = False
        except Exception:
            use_native = False

        if use_native:
            logger.info("Starting in native window mode")
        else:
            logger.info("Starting in browser mode — open http://localhost:8080")

        import nicegui  # noqa: E402
        nicegui.ui.run(
            title="从容猛攻助手",
            native=use_native,
            window_size=(480, 720),
            reload=False,
            port=8080 if not use_native else None,
            host="127.0.0.1",
        )

    except Exception:
        tb = traceback.format_exc()
        logger.error(f"Fatal startup error:\n{tb}")
        CRASH_LOG.write_text(tb, encoding="utf-8")
        print(f"\nFATAL ERROR — details in {CRASH_LOG}", file=sys.stderr)
        print(tb, file=sys.stderr)
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
