from pathlib import Path

CONFIG_LOCATION: Path = Path.home() / ".config/offtoot"
TOKEN_LOCATION: Path = CONFIG_LOCATION / "token"
URL_LOCATION: Path = CONFIG_LOCATION / "url"
APP_LOCATION: Path = CONFIG_LOCATION / "app"
STATE_LOCATION: Path = Path.home() / ".local/share/offtoot"
STORAGE_LOCATION: Path = Path.home() / ".cache/offtoot"

CONFIG_LOCATION.mkdir(parents=True, exist_ok=True)
STATE_LOCATION.mkdir(parents=True, exist_ok=True)
STORAGE_LOCATION.mkdir(parents=True, exist_ok=True)

MAX_MEDIA_LEVEL = 0
MEDIA_SIZE = "preview"
