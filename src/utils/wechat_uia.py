from __future__ import annotations

import time
import random
import subprocess
from pathlib import Path

import uiautomation as auto
from loguru import logger


class WeChatUIA:
    """Wraps Windows UI Automation calls to the WeChat PC client."""

    def __init__(self, window_title: str = "微信") -> None:
        self._window_title = window_title
        self._window = None

    def is_available(self) -> bool:
        """Check if WeChat window exists and is accessible."""
        try:
            self._window = auto.WindowControl(Name=self._window_title, ClassName="WeChatMainWndForPC")
            return self._window.Exists(maxSearchSeconds=1)
        except Exception as e:
            logger.debug(f"WeChat UIA check failed: {e}")
            return False

    def _ensure_window(self) -> bool:
        if self._window is None or not self._window.Exists():
            return self.is_available()
        return True

    def get_recent_senders(self) -> list[str]:
        """Return list of contact names visible in the WeChat chat list."""
        if not self._ensure_window():
            logger.warning("WeChat window not available")
            return []

        senders: list[str] = []
        try:
            session_list = self._window.ListControl(
                Name="会话", searchDepth=5, maxSearchSeconds=1
            )
            if not session_list.Exists():
                session_list = self._window.ListControl(
                    searchDepth=5, maxSearchSeconds=1
                )

            items = session_list.GetChildren()
            for item in items:
                name = item.Name.strip()
                if name and name != "会话":
                    senders.append(name)
        except Exception as e:
            logger.error(f"Failed to enumerate chat list: {e}")

        logger.debug(f"Found {len(senders)} recent senders: {senders[:5]}...")
        return senders

    def open_chat(self, contact_name: str) -> bool:
        """Open a chat with the given contact by clicking their name in the list."""
        if not self._ensure_window():
            logger.warning("WeChat window not available")
            return False

        try:
            self._window.SetFocus()
            time.sleep(0.1)

            session_list = self._window.ListControl(searchDepth=5, maxSearchSeconds=1)
            target = session_list.ListItemControl(Name=contact_name, maxSearchSeconds=1)
            if not target.Exists():
                # Try scroll and search
                target = self._window.ListItemControl(
                    Name=contact_name, maxSearchSeconds=2
                )

            if target.Exists():
                target.Click()
                time.sleep(0.3)
                logger.info(f"Opened chat with: {contact_name}")
                return True
            else:
                logger.warning(f"Contact not found in chat list: {contact_name}")
                return False
        except Exception as e:
            logger.error(f"Failed to open chat '{contact_name}': {e}")
            return False

    def get_last_message(self, contact_name: str) -> str:
        """Get the last message text from a specific chat in the list."""
        if not self._ensure_window():
            return ""

        try:
            session_list = self._window.ListControl(searchDepth=5, maxSearchSeconds=1)
            items = session_list.GetChildren()
            for item in items:
                name = item.Name.strip()
                if contact_name in name or name == contact_name:
                    return name.replace(contact_name, "").strip()
        except Exception as e:
            logger.error(f"Failed to get message for '{contact_name}': {e}")
        return ""

    def send_text(self, text: str) -> bool:
        """Type text into the chat input and press Enter to send."""
        if not self._ensure_window():
            logger.warning("WeChat window not available for send")
            return False

        try:
            self._window.SetFocus()
            time.sleep(0.1)

            edit = self._window.EditControl(searchDepth=8, maxSearchSeconds=1)
            if not edit.Exists():
                logger.error("Chat input EditControl not found")
                return False

            edit.Click()
            time.sleep(0.05)
            edit.SetValue("")

            for char in text:
                edit.SendKeys(char)
                time.sleep(random.uniform(0.03, 0.08))

            time.sleep(0.1)
            auto.SendKeys("{Enter}")
            logger.info(f"Sent text ({len(text)} chars)")
            return True
        except Exception as e:
            logger.error(f"Failed to send text: {e}")
            return False

    def send_image(self, image_path: Path) -> bool:
        """Copy image to clipboard and paste into WeChat, then send."""
        if not self._ensure_window():
            logger.warning("WeChat window not available for image send")
            return False

        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            return False

        try:
            # Use PowerShell to copy image to clipboard
            ps_cmd = (
                f'Add-Type -AssemblyName System.Windows.Forms;'
                f'[Windows.Forms.Clipboard]::SetImage('
                f'[System.Drawing.Image]::FromFile("{image_path}")'
                f')'
            )
            subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                timeout=5,
            )

            time.sleep(0.2)

            self._window.SetFocus()
            time.sleep(0.1)

            edit = self._window.EditControl(searchDepth=8, maxSearchSeconds=1)
            if edit.Exists():
                edit.Click()
                time.sleep(0.05)

            auto.SendKeys("{Ctrl}v")
            time.sleep(0.3)
            auto.SendKeys("{Enter}")
            logger.info(f"Sent image: {image_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to send image: {e}")
            return False

    def dump_tree(self, label: str = "") -> None:
        """Debug helper: dump the UIA control tree of the WeChat window."""
        if not self._ensure_window():
            logger.warning("WeChat window not available for dump")
            return

        def _dump(control, depth: int = 0, max_depth: int = 4) -> None:
            if depth > max_depth:
                return
            indent = "  " * depth
            logger.debug(
                f"{indent}[{control.ControlTypeName}] "
                f"Name='{control.Name}' "
                f"ClassName='{control.ClassName}' "
                f"AutomationId='{control.AutomationId}'"
            )
            try:
                for child in control.GetChildren():
                    _dump(child, depth + 1, max_depth)
            except Exception:
                pass

        logger.info(f"=== UIA Tree Dump: {label} ===")
        _dump(self._window)
