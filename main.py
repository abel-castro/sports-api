import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from sports_api.main import app  # noqa: E402

__all__ = ["app"]
