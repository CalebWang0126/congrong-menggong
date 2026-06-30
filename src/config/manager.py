import json
from pathlib import Path
from typing import Any

DEFAULT_CONFIG: dict = {
    "preset_reply": "在打排位，这把很快，打完找你 ❤️",
    "auto_reply": True,
    "screenshot": True,
    "show_content": True,
    "targets": [],
    "wechat_window_title": "微信",
}


class ConfigManager:
    def __init__(self, data_dir: Path | str | None = None) -> None:
        if data_dir is None:
            data_dir = Path.home() / "AppData" / "Roaming" / "congrong-menggong"
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._config_path = self._data_dir / "config.json"
        self._config: dict = {}

    @property
    def config(self) -> dict:
        return self._config

    def load(self) -> dict:
        if self._config_path.exists():
            self._config = json.loads(self._config_path.read_text(encoding="utf-8"))
        else:
            self._config = dict(DEFAULT_CONFIG)
            self.save(self._config)
        return self._config

    def save(self, config: dict) -> None:
        self._config = dict(config)
        self._config_path.write_text(
            json.dumps(self._config, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._config[key] = value
        self.save(self._config)
