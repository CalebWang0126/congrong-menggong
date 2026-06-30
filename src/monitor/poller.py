# src/monitor/poller.py
from __future__ import annotations

import asyncio
import hashlib
from typing import Callable

from loguru import logger

from src.config.manager import ConfigManager
from src.monitor.matcher import MsgMatcher
from src.utils.wechat_uia import WeChatUIA


class Monitor:
    """Polls WeChat for new messages from monitored contacts."""

    POLL_INTERVAL: float = 0.5  # seconds

    def __init__(
        self,
        wechat: WeChatUIA,
        matcher: MsgMatcher,
        config: ConfigManager,
    ) -> None:
        self._wechat = wechat
        self._matcher = matcher
        self._config = config
        self._seen: set[str] = set()
        self._running = False
        self._task: asyncio.Task | None = None
        self._on_message: Callable[[dict], None] | None = None

    @property
    def is_running(self) -> bool:
        return self._running

    def _fingerprint(self, sender: str, content: str) -> str:
        raw = f"{sender.strip()}::{content.strip()}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def poll(self) -> list[dict]:
        """Single poll cycle. Returns new matched messages."""
        if not self._wechat.is_available():
            logger.debug("WeChat not available, skipping poll")
            return []

        new_messages: list[dict] = []
        show_content = self._config.get("show_content", True)

        senders = self._wechat.get_recent_senders()
        if not senders:
            return []

        for sender in senders:
            matched = self._matcher.match(sender)
            if matched is None:
                continue

            raw_last = self._wechat.get_last_message(sender)

            # The sender string from WeChat may include the last message preview
            # e.g., "宝贝老婆几点回家" -> sender="宝贝老婆", preview="几点回家"
            if raw_last and raw_last != sender:
                content = raw_last
            else:
                content = "(无法读取消息内容)"

            fp = self._fingerprint(sender, content)
            if fp in self._seen:
                continue
            self._seen.add(fp)

            entry = {
                "sender": matched.get("nickname", sender),
                "content": content if show_content else f"收到 1 条新消息",
                "raw_content": content,
                "matched_target": matched,
            }
            new_messages.append(entry)
            logger.info(f"New message from {entry['sender']}")

        return new_messages

    async def _loop(self) -> None:
        logger.info("Monitor loop started")
        while self._running:
            try:
                msgs = self.poll()
                for msg in msgs:
                    if self._on_message:
                        self._on_message(msg)
            except Exception as e:
                logger.error(f"Monitor poll error: {e}")
            await asyncio.sleep(self.POLL_INTERVAL)
        logger.info("Monitor loop stopped")

    def start(self, on_message_callback: Callable[[dict], None]) -> None:
        """Begin async polling. `on_message_callback` receives each new message dict."""
        self._on_message = on_message_callback
        self._running = True
        self._task = asyncio.create_task(self._loop())

    def stop(self) -> None:
        """Stop the polling loop."""
        self._running = False
        self._seen.clear()
        if self._task and not self._task.done():
            self._task.cancel()
            logger.info("Monitor task cancelled")
