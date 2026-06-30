from __future__ import annotations

from datetime import datetime
from typing import Any

from nicegui import ui
from loguru import logger

from src.config.manager import ConfigManager
from src.monitor.poller import Monitor
from src.reply.engine import ReplyEngine


class MessageStore:
    """Reactive message log for the GUI."""

    def __init__(self) -> None:
        self.messages: list[dict[str, Any]] = []
        self._refresh_ui = None

    def bind(self, refresh_fn) -> None:
        self._refresh_ui = refresh_fn

    def add(self, sender: str, content: str) -> None:
        ts = datetime.now().strftime("%H:%M")
        self.messages.append({
            "time": ts,
            "sender": sender,
            "content": content,
        })
        logger.info(f"[MSG] {ts} {sender}: {content}")
        if self._refresh_ui:
            self._refresh_ui()


def create_app(
    config: ConfigManager,
    monitor: Monitor,
    reply_engine: ReplyEngine,
) -> None:
    store = MessageStore()

    # --- State ---
    monitoring = False

    def on_new_message(msg: dict) -> None:
        store.add(msg["sender"], msg["content"])
        if config.get("auto_reply"):
            preset = config.get("preset_reply", "")
            with_screenshot = config.get("screenshot", False)
            contact = msg["matched_target"].get("nickname", msg["sender"])
            reply_engine.send(contact, preset, with_screenshot=with_screenshot)

    def toggle_monitoring():
        nonlocal monitoring
        monitoring = not monitoring
        if monitoring:
            monitor.start(on_new_message)
            status_label.set_text("🟢 监听中")
            start_btn.set_text("停止监听")
            start_btn.props("color=red")
        else:
            monitor.stop()
            status_label.set_text("⏸ 已停止")
            start_btn.set_text("开始监听")
            start_btn.props("color=green")

    def handle_manual_send():
        text = manual_input.value.strip()
        if not text:
            ui.notify("请输入回复内容", type="warning")
            return
        targets = config.get("targets", [])
        if not targets:
            ui.notify("请先添加监控对象", type="warning")
            return
        contact = targets[0]["nickname"]
        with_screenshot = config.get("screenshot", False)
        success = reply_engine.send(contact, text, with_screenshot=with_screenshot)
        if success:
            ui.notify(f"已发送给 {contact}")
            manual_input.set_value("")
        else:
            ui.notify("发送失败，请检查微信是否打开", type="error")

    def save_config():
        config.save({
            "preset_reply": preset_input.value,
            "auto_reply": auto_reply_switch.value,
            "screenshot": screenshot_switch.value,
            "show_content": show_content_switch.value,
            "targets": config.get("targets", []),
            "wechat_window_title": config.get("wechat_window_title", "微信"),
        })
        ui.notify("配置已保存", type="positive")

    def build_message_list():
        """Rebuild the message display area."""
        message_container.clear()
        with message_container:
            for msg in store.messages:
                ui.label(f"{msg['time']} {msg['sender']}：{msg['content']}")

    store.bind(build_message_list)

    # --- UI Layout ---
    with ui.column().classes("w-full max-w-2xl mx-auto p-4 gap-4"):

        ui.label("🎮 从容猛攻助手").classes("text-2xl font-bold text-center")

        # Config Section
        with ui.card().classes("w-full"):
            ui.label("📋 预设回复话术").classes("text-sm font-medium")
            preset_input = ui.textarea(
                value=config.get("preset_reply", ""),
            ).classes("w-full").props("outlined rows=2")

            ui.label("⚙ 选项").classes("text-sm font-medium mt-2")
            with ui.row().classes("gap-4"):
                auto_reply_switch = ui.switch(
                    "自动回复", value=config.get("auto_reply", True)
                )
                screenshot_switch = ui.switch(
                    "截屏", value=config.get("screenshot", True)
                )
                show_content_switch = ui.switch(
                    "展示消息内容", value=config.get("show_content", True)
                )

            ui.button("保存配置", on_click=save_config).props("flat size=sm")

        # Monitoring Controls
        with ui.card().classes("w-full"):
            ui.label("👤 监控对象").classes("text-sm font-medium")
            targets = config.get("targets", [])
            if targets:
                for t in targets:
                    ui.label(f"  • {t['nickname']}").classes("text-sm")
            else:
                ui.label("  （未添加监控对象，请在 config.json 中手动添加）").classes("text-xs text-gray-500")

            status_label = ui.label("⏸ 已停止").classes("text-sm mt-2")
            with ui.row().classes("gap-2 mt-2"):
                start_btn = ui.button(
                    "开始监听", on_click=toggle_monitoring
                ).props("color=green")

        # Message Stream
        with ui.card().classes("w-full"):
            ui.label("📨 消息").classes("text-sm font-medium")
            message_container = ui.column().classes("w-full max-h-64 overflow-y-auto")

        # Manual Reply
        with ui.card().classes("w-full"):
            ui.label("✏ 快速回复").classes("text-sm font-medium")
            with ui.row().classes("w-full gap-2 items-center"):
                manual_input = ui.input(placeholder="手动打字回复…").classes("flex-grow")
                ui.button("发送", on_click=handle_manual_send).props("color=blue")
