import json
import tempfile
from pathlib import Path
import pytest
from src.config.manager import ConfigManager, DEFAULT_CONFIG


class TestConfigManager:
    def test_default_config_structure(self):
        """DEFAULT_CONFIG must have all required keys."""
        assert "preset_reply" in DEFAULT_CONFIG
        assert "auto_reply" in DEFAULT_CONFIG
        assert "screenshot" in DEFAULT_CONFIG
        assert "show_content" in DEFAULT_CONFIG
        assert "targets" in DEFAULT_CONFIG
        assert isinstance(DEFAULT_CONFIG["auto_reply"], bool)
        assert isinstance(DEFAULT_CONFIG["screenshot"], bool)
        assert isinstance(DEFAULT_CONFIG["show_content"], bool)
        assert isinstance(DEFAULT_CONFIG["targets"], list)

    def test_creates_config_file_on_first_load(self):
        """First load() with no existing file creates one from defaults."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = ConfigManager(data_dir=tmp)
            result = cfg.load()
            config_path = Path(tmp) / "config.json"
            assert config_path.exists()
            assert result["preset_reply"] == DEFAULT_CONFIG["preset_reply"]

    def test_load_returns_existing_config(self):
        """load() reads an existing JSON file."""
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.json"
            custom = {**DEFAULT_CONFIG, "preset_reply": "自定义回复"}
            config_path.write_text(json.dumps(custom, ensure_ascii=False, indent=2))
            cfg = ConfigManager(data_dir=tmp)
            result = cfg.load()
            assert result["preset_reply"] == "自定义回复"

    def test_save_writes_and_load_reads_back(self):
        """save() then load() returns the same data."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = ConfigManager(data_dir=tmp)
            modified = {**DEFAULT_CONFIG, "auto_reply": False, "screenshot": False}
            cfg.save(modified)
            result = cfg.load()
            assert result["auto_reply"] is False
            assert result["screenshot"] is False

    def test_get_returns_value_and_default(self):
        """get() retrieves values with fallback."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = ConfigManager(data_dir=tmp)
            cfg.load()
            assert cfg.get("auto_reply") is True
            assert cfg.get("nonexistent", "fallback") == "fallback"

    def test_set_modifies_and_persists(self):
        """set() updates a single key and persists to disk."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = ConfigManager(data_dir=tmp)
            cfg.load()
            cfg.set("preset_reply", "新话术")
            # Reload from disk to verify persistence
            cfg2 = ConfigManager(data_dir=tmp)
            assert cfg2.load()["preset_reply"] == "新话术"

    def test_config_property_reflects_current_state(self):
        """config property is live after load."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = ConfigManager(data_dir=tmp)
            cfg.load()
            assert cfg.config["preset_reply"] == DEFAULT_CONFIG["preset_reply"]
