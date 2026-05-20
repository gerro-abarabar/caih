import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict

from datafetch.exam_model import Exam


def get_filename(exam: Exam):
    """Return the recommended location for the user data file.

    We place the file in the project root (two levels up from this file:
    src/pages/user.py -> project_root/prev_exams/subject_i.json).
    """
    # 1. Establish the correct, absolute path to the target directory
    project_root = Path(__file__).resolve().parents[2]
    target_dir = project_root / "prev_exams"

    # Ensure the directory exists so os.listdir doesn't throw an error
    target_dir.mkdir(parents=True, exist_ok=True)

    # 2. Find a unique filename
    i = 0
    base_name = exam.subject

    while True:
        # Create the candidate filename for this iteration
        candidate_name = f"{base_name}_{i}.json" if i > 0 else f"{base_name}.json"

        # Check if this specific file already exists in the folder
        if candidate_name not in os.listdir(target_dir):
            return target_dir / candidate_name

        i += 1


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
    exam.saved = True
    print("Initiated saving exam...")
    filename = get_filename(exam)
    print("Found a good filename:", filename)
    _atomic_write(filename, exam.model_dump())
    print("Successfully saved it")


def get_exam(exam_name):
    with open(f"./prev_exams/{exam_name}", "r") as f:
        return Exam(**json.load(f))


def get_exam_files():
    return os.listdir("./prev_exams/")
