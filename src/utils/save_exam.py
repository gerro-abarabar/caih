import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict

from datafetch.exam_model import Exam


def get_data_file(exam: Exam):
    """Return the recommended location for the user data file.

    We place the file in the project root (two levels up from this file:
    src/pages/user.py -> project_root/user_data.json). If you prefer another
    location, change this helper.
    """
    i = 0
    filename = exam.subject
    while True:
        if filename not in os.listdir("./prev_exams"):
            filename = f"{filename}_{i}"
            break
        i += 1
    return Path(__file__).resolve().parents[2] / "prev_exams" / f"{filename}.json"


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


def save_exam(exam):
    filename = get_data_file(exam)
    _atomic_write(filename, exam.model_dump())
