"""Resolves persistent (writable) and bundled (read-only) file locations.

Keeps user data outside of the PyInstaller onefile bundle, so it survives
app restarts, PC reboots, and rebuilds/updates of the exe.
"""
import os
import sys
from pathlib import Path

APP_DATA_DIRNAME = "LoaBuilds"
PLACEHOLDER_ICON = "placeholder.png"


def get_app_data_dir() -> Path:
    base = Path(os.environ.get("APPDATA", str(Path.home()))) / APP_DATA_DIRNAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_db_path() -> Path:
    return get_app_data_dir() / "loa_builds.db"


def get_user_icons_dir() -> Path:
    d = get_app_data_dir() / "icons"
    d.mkdir(parents=True, exist_ok=True)
    return d


def resource_path(relative: str) -> Path:
    """Resolves a bundled read-only resource, both when frozen (PyInstaller
    onefile extracts to sys._MEIPASS) and when running as a plain script."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base / relative


def resolve_class_icon(icon_filename: str | None) -> Path:
    """Lookup order: user override in %APPDATA% -> bundled default -> placeholder."""
    if icon_filename:
        user_path = get_user_icons_dir() / icon_filename
        if user_path.exists():
            return user_path
        bundled_path = resource_path(f"icons/{icon_filename}")
        if bundled_path.exists():
            return bundled_path
    return resource_path(f"icons/{PLACEHOLDER_ICON}")
