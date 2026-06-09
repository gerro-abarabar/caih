import json
import tempfile
from pathlib import Path
from typing import Any, Dict

import streamlit as st

DEFAULT_DATA: Dict[str, Any] = {
    "version": "v1",
    "user": {
        "name": "John Doe",
        "username": "johndoe",
        "email": "john.doe@example.com",
        "bio": "This is a sample bio. Update it to tell others about yourself.",
        "avatar_url": "",
        "preferences": {
            "theme": "light",
            "notifications": True,
        },
    },
    "progress": {
        "exams_taken": 0,
        "lessons_completed": 0,
        "flashcards_reviewed": 0,
        "subjects": {},
    },
    "meta": {
        "created_by": "src/pages/user.py",
        "description": "User profile data for the Streamlit app (extendable)",
    },
}


def get_data_file() -> Path:
    """Return the recommended location for the user data file.

    We place the file in the project root (two levels up from this file:
    src/pages/user.py -> project_root/user_data.json). If you prefer another
    location, change this helper.
    """
    return Path(__file__).resolve().parents[2] / "user_data.json"


def _atomic_write(path: Path, data: Dict[str, Any]) -> None:
    """Write JSON to `path` atomically by writing to a temp file then replacing.

    This avoids corruption if the app is interrupted while writing.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # Write to a temp file in the same directory then atomically replace
    with tempfile.NamedTemporaryFile(
        "w", delete=False, dir=path.parent, encoding="utf-8"
    ) as tf:
        json.dump(data, tf, indent=2, ensure_ascii=False)
        temp_path = Path(tf.name)
    temp_path.replace(path)


def load_user_data(path: Path) -> Dict[str, Any]:
    """Load user data from disk. If missing or corrupted, write and return defaults."""
    if not path.exists():
        # create file with defaults
        _atomic_write(path, DEFAULT_DATA)
        return DEFAULT_DATA.copy()

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Validate minimal shape and fill missing keys
        if not isinstance(data, dict):
            raise ValueError("data is not a dict")

        if "user" not in data or not isinstance(data["user"], dict):
            data["user"] = DEFAULT_DATA["user"].copy()

        return data
    except Exception as e:
        st.error(f"Failed to load user data ({e}). Restoring defaults.")
        _atomic_write(path, DEFAULT_DATA)
        return DEFAULT_DATA.copy()


def save_user_data(path: Path, data: Dict[str, Any]) -> None:
    """Persist user data atomically."""
    _atomic_write(path, data)


def evolve_subject_progress(
    user_data: Dict[str, Any], subject: str, increment: float = 1.0
) -> None:
    """Helper to update progress for a specific subject."""
    user_data["progress"]["subjects"][subject] = (
        user_data["progress"]["subjects"].get(subject, 0) + increment
    )
    _atomic_write(get_data_file(), user_data)


def increment_exams_taken(user_data: Dict[str, Any]) -> None:
    """Helper to increment the total exams taken."""
    user_data["progress"]["exams_taken"] += 1
    _atomic_write(get_data_file(), user_data)
