import json
from pathlib import Path

import platformdirs

from constants import APP_SLUG, CONFIG_FILENAME, DEFAULT_NOTES_DIR

class ConfigManager:
    APP_SLUG = APP_SLUG
    CONFIG_FILENAME = CONFIG_FILENAME
    DEFAULT_NOTES_DIR = DEFAULT_NOTES_DIR
    
    def __init__(self) -> None:
        self.config_dir = Path(platformdirs.user_config_dir(self.APP_SLUG, roaming=True, appauthor=False))
        self.config_path = self.config_dir / self.CONFIG_FILENAME
        
        self._config: dict[str, str] = {
            "notes_directory": self.DEFAULT_NOTES_DIR,
        }
        
        self._load()


    def _load(self) -> None:
        if not self.config_path.exists():
            self._save()
            print(f"Config created at: {self.config_path}")
            return

        with self.config_path.open("r", encoding="utf-8") as f:
            loaded = json.load(f)
            self._config.update(loaded)

    def _save(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    @property
    def notes_directory(self) -> Path:
        path_str = self._config.get("notes_directory", self.DEFAULT_NOTES_DIR)
        return Path(path_str).resolve()

    @notes_directory.setter
    def notes_directory(self, value: str | Path) -> None:
        self._config["notes_directory"] = str(Path(value).resolve())
        self._save()

    def save(self) -> None:
        self._save()