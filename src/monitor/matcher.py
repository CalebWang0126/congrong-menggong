from __future__ import annotations


class MsgMatcher:
    def __init__(self, targets: list[dict]) -> None:
        self._targets: list[dict] = targets

    def update_targets(self, targets: list[dict]) -> None:
        self._targets = targets

    def match(self, sender: str) -> dict | None:
        clean = sender.strip()
        for target in self._targets:
            remark = target.get("remark", "").strip()
            nickname = target.get("nickname", "").strip()
            if remark and clean == remark:
                return target
            if nickname and clean == nickname:
                return target
        return None
