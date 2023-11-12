from pathlib import Path

TOKEN_LOCATION: Path = Path.home() / ".local/share/passwords/offtoot/token"
URL_LOCATION: Path = Path.home() / ".local/share/passwords/offtoot/url"
STATE_LOCATION: Path = Path.home() / ".local/share/offtoot"
STORAGE_LOCATION: Path = STATE_LOCATION / "store"

STATE_LOCATION.mkdir(parents=True, exist_ok=True)
