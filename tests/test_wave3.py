"""Wave 3: config schema v2 and the local secret-scan hook."""
import json
import subprocess
import sys

from wattpdl import config


class TestConfigV2:
    def test_fresh_config_has_version_2(self, tmp_path, monkeypatch):
        monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")
        assert config.load_config()["version"] == 2

    def test_old_config_is_migrated(self, tmp_path, monkeypatch):
        monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")
        (tmp_path / "config.json").write_text(json.dumps({"file_format": "3"}), encoding="utf-8")
        loaded = config.load_config()
        assert loaded["version"] == 2
        assert loaded["file_format"] == "3"

    def test_version_1_is_migrated(self, tmp_path, monkeypatch):
        monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")
        (tmp_path / "config.json").write_text(json.dumps({"version": 1, "file_format": "2"}), encoding="utf-8")
        assert config.load_config()["version"] == 2

    def test_save_config_keeps_version(self, tmp_path, monkeypatch):
        monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")
        config.save_config(ui_lang="id")
        data = json.loads((tmp_path / "config.json").read_text(encoding="utf-8"))
        assert data["version"] == 2
        assert data["ui_lang"] == "id"


class TestSecretScanHook:
    def test_clean_file_passes(self, tmp_path):
        target = tmp_path / "clean.py"
        target.write_text("token = 'placeholder'\n", encoding="utf-8")
        result = subprocess.run([sys.executable, "scripts/scan_secrets.py", str(target)],
                                capture_output=True, text=True)
        assert result.returncode == 0

    def test_fake_token_fails(self, tmp_path):
        target = tmp_path / "leak.txt"
        target.write_text("key=" + "gh" + "p_" + "A" * 25 + "\n", encoding="utf-8")
        result = subprocess.run([sys.executable, "scripts/scan_secrets.py", str(target)],
                                capture_output=True, text=True)
        assert result.returncode == 1
        assert "GitHub token" in result.stdout
